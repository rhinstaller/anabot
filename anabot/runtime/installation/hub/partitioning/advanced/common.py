from anabot.runtime.translate import tr

def schema_name(schema=None):
    SCHEMAS = {
        'native' : tr("Standard Partition"),
        'btrfs' : tr("Btrfs"),
        'lvm' : tr("LVM"),
        'raid' : tr("RAID"),
        'lvm thinp' : tr("LVM Thin Provisioning")
    }
    if schema is not None:
        return SCHEMAS[schema]
    return SCHEMAS.values()
