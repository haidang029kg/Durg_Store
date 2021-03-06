from django.db import transaction

from apps.common.logger import logger


def custom_bulk_sync(new_models, key_fields, filters, batch_size=None, fields=None, skip_creates=False,
                     skip_updates=False,
                     skip_deletes=False):
    """ Combine bulk create, update, and delete.  Make the DB match a set of in-memory objects.

    `new_models`: Django ORM objects that are the desired state.  They may or may not have `id` set.
    `key_fields`: Identifying attribute name(s) to match up `new_models` items with database rows.  If a foreign key
            is being used as a key field, be sure to pass the `fieldname_id` rather than the `fieldname`.
    `filters`: Q() filters specifying the subset of the database to work in.  Use `None` or `[]` if you want to sync against the entire table.
    `batch_size`: passes through to Django `bulk_create.batch_size` and `bulk_update.batch_size`, and controls
            how many objects are created/updated per SQL query.
    `fields`: (optional) list of fields to update. If not set, will sync all fields that are editable and not auto-created.
    `skip_creates`: If truthy, will not perform any object creations needed to fully sync. Defaults to not skip.
    `skip_updates`: If truthy, will not perform any object updates needed to fully sync. Defaults to not skip.
    `skip_deletes`: If truthy, will not perform any object deletions needed to fully sync. Defaults to not skip.
    """
    db_class = new_models[0].__class__

    if fields is None:
        # Get a list of fields that aren't PKs and aren't editable (e.g. auto_add_now) for bulk_update
        fields = [field.name
                  for field in db_class._meta.fields
                  if not field.primary_key and not field.auto_created and field.editable]

    with transaction.atomic():
        objs = db_class.all_objects.all()
        if filters:
            objs = objs.filter(filters)
        objs = objs.only("pk", *key_fields).select_for_update()

        def get_key(obj):
            return tuple(getattr(obj, k) for k in key_fields)

        obj_dict = {get_key(obj): obj for obj in objs}

        new_objs = []
        existing_objs = []
        for new_obj in new_models:
            old_obj = obj_dict.pop(get_key(new_obj), None)
            if old_obj is None:
                # This is a new object, so create it.
                # Make sure the primary key field is clear.
                new_obj.pk = None
                new_objs.append(new_obj)
            else:
                new_obj.id = old_obj.id
                existing_objs.append(new_obj)

        if not skip_creates:
            db_class.objects.bulk_create(new_objs, batch_size=batch_size)

        if not skip_updates:
            db_class.all_objects.bulk_update(existing_objs, fields=fields, batch_size=batch_size)

        if not skip_deletes:
            # delete stale objects
            objs.filter(pk__in=[_.pk for _ in list(obj_dict.values())]).update(is_removed=True)

        assert len(existing_objs) == len(new_models) - len(new_objs)

        stats = {
            "created": 0 if skip_creates else len(new_objs),
            "updated": 0 if skip_updates else (len(new_models) - len(new_objs)),
            "deleted": 0 if skip_deletes else len(obj_dict)
        }

        logger.debug(
            "{}: {} created, {} updated, {} deleted.".format(
                db_class.__name__, stats["created"], stats["updated"], stats["deleted"]
            )
        )

    return {"stats": stats}
