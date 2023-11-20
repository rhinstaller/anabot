import re
from anabot.runtime.translate import tr
from anabot.conditions import is_distro_version
from anabot.runtime.functions import getnode, getsibling
from anabot.runtime.errors import TimeoutError

def schema_name(schema=None):
    SCHEMAS = {
        'native' : tr("Standard Partition"),
        'btrfs' : tr("Btrfs"),
        'lvm' : tr("LVM"),
        'raid' : tr("RAID"),
        'lvm thinp' : tr("LVM Thin Provisioning")
    }
    if schema is not None:
        try:
            return SCHEMAS[schema]
        except KeyError as exc:
            raise ValueError(f"Unsupported schema name: '{schema}'") from exc
    return SCHEMAS.values()

def raid_name(raid_level=None, drop_span=True):
    if is_distro_version('rhel', 7):
        LEVELS = {
            "none"   : tr("None"),
            "RAID0"  : tr("RAID0 <span foreground=\"grey\">(Performance)</span>"),
            "RAID1"  : tr("RAID1 <span foreground=\"grey\">(Redundancy)</span>"),
            "RAID4"  : tr("RAID4 <span foreground=\"grey\">(Error Checking)</span>"),
            "RAID5"  : tr("RAID5 <span foreground=\"grey\">(Distributed Error Checking)</span>"),
            "RAID6"  : tr("RAID6 <span foreground=\"grey\">(Redundant Error Checking)</span>"),
            "RAID10" : tr("RAID10 <span foreground=\"grey\">(Performance, Redundancy)</span>"),
        }
    else:
        LEVELS = {
            "none"   : tr("None"),
            "RAID0"  : tr("RAID0"),
            "RAID1"  : tr("RAID1"),
            "RAID4"  : tr("RAID4"),
            "RAID5"  : tr("RAID5"),
            "RAID6"  : tr("RAID6"),
            "RAID10" : tr("RAID10"),
        }
    if drop_span:
        exp = re.compile(r'(.*)<span foreground=\"grey\">(.*)</span>')
        for level in LEVELS:
            LEVELS[level] = exp.sub(r"\1\2", LEVELS[level])
    if raid_level is not None:
        return LEVELS[raid_level]
    return LEVELS.values()

def check_partitioning_error(app_node):
    try:
        error_bar = getnode(app_node, "info bar", tr("Error"))
        warn_icon = getnode(error_bar, "icon", tr("Warning"))
        warn_text = getsibling(warn_icon, 1, "label")
        return (False, warn_text.text)
    except TimeoutError:
        return True
