from datetime import datetime
import pytz

def is_dst():
    """Determine whether or not it is daylight saving time (DST)"""
    x=datetime(datetime.now().year,1,1,0,0,0, tzinfo=pytz.timezone("US/Eastern"))
    y=datetime.now(pytz.timezone("US/Eastern"))

    """if DST is not in effect, their offsets will be different"""
    return not (y.utcoffset()==x.utcoffset())


print(is_dst())