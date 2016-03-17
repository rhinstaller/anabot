import re
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

def raid_name(raid_level=None, drop_span=True):
    LEVELS = {
        "none"   : tr("None"),
        "RAID0"  : tr("RAID0 <span foreground=\"grey\">(Performance)</span>"),
        "RAID1"  : tr("RAID1 <span foreground=\"grey\">(Redundancy)</span>"),
        "RAID4"  : tr("RAID4 <span foreground=\"grey\">(Error Checking)</span>"),
        "RAID5"  : tr("RAID5 <span foreground=\"grey\">(Distributed Error Checking)</span>"),
        "RAID6"  : tr("RAID6 <span foreground=\"grey\">(Redundant Error Checking)</span>"),
        "RAID10" : tr("RAID10 <span foreground=\"grey\">(Performance, Redundancy)</span>"),
    }
    if drop_span:
        exp = re.compile(r'(.*)<span foreground=\"grey\">(.*)</span>')
        for level in LEVELS:
            LEVELS[level] = exp.sub(r"\1\2", LEVELS[level])
    if raid_level is not None:
        return LEVELS[raid_level]
    return LEVELS.values()
