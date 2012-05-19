"""
@version: 0.7
@date:    2008-08-28
@status:  beta
@author:  Stephen Ferg
@contact: http://www.ferg.org/contact_info
@license: Creative Commons Attribution License 2.0 http://creativecommons.org/licenses/by/2.0/
@see:     http://www.ferg.org/pyfdate
@note:

ABOUT PYFDATE

The purpose of pyfdate is to provide a variety of user-friendly features
for working with datetimes, doing date arithmetic, and formatting dates,
times, and periods of time.

Pyfdate doesn't attempt to be all things to all people: rather, its goal
is to make it easy to do 95% if the things that people want to do with
dates and times.

Pyfdate provides two classes:

------------------------------------------------------------------------

Time:
	- A specific point in time, identified by
	  year, month, day, hour, minute, second.
	(Python's datetime module calls this a "datetime".)

Period:
	- An amount of time, measured in days, hours, minutes, and seconds.

------------------------------------------------------------------------

In order to keep pyfdate simple, there are a number of things that it does not attempt to do.
	- Pyfdate doesn't know anything about timezones.
	- Pyfdate doesn't know anything about daylight savings time.
	- Pyfdate doesn't provide any facilities for parsing strings into date/times.
	  (It does, however, provide a useful numsplit() function which performs a kind of parsing.)
	- The smallest unit of time that Pyfdate can handle is a second.
	   It cannot be used to work with hundredths or thousandths of seconds.

INTERNATIONAL LANGUAGE SUPPORT

By default, pyfdate's language for displaying dates and times
(e.g. weekday names and month names) is American English.

If pyfdate can successfully import pyfdate_local,
the language for displaying dates and times
is taken from the pyfdate_local.py file.

Localization files are available for a number of languages.
For example: pyfdate_local_francais.py for French.

To use the file for language foobar,
simply copy pyfdate_local_foobar.py to pyfdate_local.py

And of course it is possible to customize pyfdate_local.py for any particular
language of your choice.  If you create (or correct) a localization file
for pyfdate, please share it with others by submitting it for inclusion
in the pyfdate distribution.


BACKGROUND

Many ideas for pyfdate functionality grew out of Steve Ferg's experiences with
an earlier (non-Python) program called "fdate", which provided datetime
arithmetic functionality for MS-DOS batch files. The name "pyfdate" is derived
from "Python" and "fdate".
"""
from pprint import pprint
import time, copy, sys, os, types

try:
	import datetime
except ImportError, e:
	raise AssertionError("Error importing datetime.\n"
	+"Note that pyfdate requires Python version 2.3+.\n"
	+"You are now running Python version " + sys.version)
from pprint import pprint

"""
Language-specific interface for pyfdate, for language:  American English
"""
LANG = "American English"
TimeExpressedIn24Hours = False
CivilTimeSeparator = ":"
CivilDateFormat = "m d, y"   # m=nameOfMonth  d=dayOfMonth y=year

HOUR    = "hour"
HOURS   = "hours"
MINUTE  = "minute"
MINUTES = "minutes"
SECOND  = "second"
SECONDS = "seconds"

DAY     = "day"
DAYS    = "days"
HOUR    = "hour"
HOURS   = "hours"
MINUTE  = "minute"
MINUTES = "minutes"
SECOND  = "second"
SECONDS = "seconds"

WEEK    = "week"
WEEKS   = "weeks"
MONTH   = "month"
MONTHS  = "months"
YEAR    = "year"
YEARS   = "years"

MONTH_NAMES = \
{ 1:"January"
, 2:"February"
, 3:"March"
, 4:"April"
, 5:"May"
, 6:"June"
, 7:"July"
, 8:"August"
, 9:"September"
,10:"October"
,11:"November"
,12:"December"
}

WEEKDAY_NAMES = \
{1:"Monday"
,2:"Tuesday"
,3:"Wednesday"
,4:"Thursday"
,5:"Friday"
,6:"Saturday"
,7:"Sunday"
}

#-----------------------------------------------------------------------
# make constants for month names and weekday names
# this may not work for all languages. (see below)
#-----------------------------------------------------------------------
for __monthNumber, __monthName in MONTH_NAMES.items():
	__monthName = __monthName.upper().replace("-","_")
	exec(__monthName + " = " + str(__monthNumber))

for __weekdayNumber, __weekdayName in WEEKDAY_NAMES.items():
	__weekdayName = __weekdayName.upper().replace("-","_")
	exec(__weekdayName + " = " + str(__weekdayNumber))

#-----------------------------------------------------------------------
# If a file called pyfdate_local exists, import it.
# This enables optional customization for different languages:
# German, French, Spanish, British English, etc.
#-----------------------------------------------------------------------
try: from pyfdate_local import *
except ImportError: pass

#---------------------------------------------------------------------
#   set up some constants
#---------------------------------------------------------------------
NEXT      = "NEXT"
NEAREST   = "NEAREST"
PREVIOUS  = "PREVIOUS"

SECONDS_IN_MINUTE  = 60
MINUTES_IN_HOUR    = 60
HOURS_IN_DAY       = 24
SECONDS_IN_HOUR    = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
SECONDS_IN_DAY     = SECONDS_IN_HOUR   * HOURS_IN_DAY
MINUTES_IN_DAY     = MINUTES_IN_HOUR   * HOURS_IN_DAY

NORMAL_DAYS_IN_MONTH = \
	{  1:31 # JAN
	,  2:28 # FEB  # does not apply to leap years
	,  3:31 # MAR
	,  4:30 # APR
	,  5:31 # MAY
	,  6:30 # JUN
	,  7:31 # JUL
	,  8:31 # AUG
	,  9:30 # SEP
	, 10:31 # OCT
	, 11:30 # NOV
	, 12:31 # DEC
	}


####################################################################################
#
#            class Period
#
####################################################################################

class Period:
	"""
	A pyfdate.Period is an amount of time.

	pyfdate.Period performs a function similar to the standard library datetime.timedelta.
	pyfdate.Period, however, is implemented differently than the datetime.timedelta class.
	pyfdate.Period stores only a single value: self.period_seconds.
	This may be a positive or negative value.

	pyfdate.Period objects (like datetime.timedelta objects) are used to do date
	arithmetic.  But since pyfdate.Time provides more sophisticated date
	arithmetic features than datetime.datetime, pyfdate. Periods are probably
	more widely used for their display capabilities than for their date
	arithmetic capabilities.
	"""
	#-----------------------------------------------------------------------------------
	#           CONSTRUCTOR
	#-----------------------------------------------------------------------------------
	def __init__(self, arg1=0,hours=0,minutes=0,seconds=0):
		"""
		Thhe constructor of a Period object.

		Constructor expects arguments of:
			- a series of positional arguments: [days [, hours[,minutes[,seconds]]]], or
			- a datetime.timedelta object, or
			- a pyfdate.Period object
		@rtype: Period
		"""
		if isinstance(arg1, datetime.timedelta):
			# first argument is a timedelta.  Ignore the other args.
			timedelta = arg1
			self.period_seconds = timedelta.seconds + (timedelta.days * SECONDS_IN_DAY)
			return

		if isinstance(arg1, Period):
			# first argument is a Period.  Ignore the other args.
			self.period_seconds = copy.deepcopy(arg1.period_seconds)
			return

		# else, arguments represent days, hours, minutes, seconds in a period.
		days = arg1
		self.period_seconds = (
				(days    * SECONDS_IN_DAY   )
			+ (hours   * SECONDS_IN_HOUR  )
			+ (minutes * SECONDS_IN_MINUTE)
			+ seconds   )


	#-----------------------------------------------------------------------------------
	#           __abs__
	#-----------------------------------------------------------------------------------
	def __abs__(self):
		"""
		Returns a clone of myself, with my absolute value.
		@return: a clone of myself, with my absolute value
		@rtype: Period
		"""
		return Period(0,0,0,abs(self.period_seconds))

	#-----------------------------------------------------------------------------------
	#           __add__
	#-----------------------------------------------------------------------------------
	def __add__(self, arg):
		"""
		Add one period to another.
		@return: a new Period object
		@rtype: Period
		"""
		if isinstance(arg, Period): pass # no problem
		else:
			raise AssertionError("Cannot add a "
				+ arg.__class__.__name__ + " object to a Period object.")

		return Period(0,0,0, self.period_seconds + arg.period_seconds)

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __eq__(self,arg):
		"""
		Compare two Period objects for equality.
		@rtype: boolean
		"""
		if isinstance(arg, Period): pass # no problem
		else:
			raise AssertionError("Cannot compare Period object with "
					+ arg.__class__.__name__ + " object.")

		if self.period_seconds == arg.period_seconds: return True
		return False

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __ge__(self,arg):
		"""
		Compares two Period objects to determine if one is greater than,
		or equal to, the other.
		@rtype: boolean
		"""
		if self.__gt__(arg): return True
		if self.__eq__(arg): return True
		return False

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __gt__(self,arg):
		"""
		Compares two Period objects to determine if one is greater than the other.
		@rtype: boolean
		"""
		if isinstance(arg, Period): pass # no problem
		else:
			raise AssertionError("Cannot compare Period object with "
					+ arg.__class__.__name__ + " object.")
		if self.period_seconds > arg.period_seconds: return True
		return False

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __le__(self,arg):
		"""
		Compares two Period objects to determine if one is less than,
		or equal to, the other.
		@rtype: boolean
		"""
		if self.__gt__(arg): return False
		return True

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __lt__(self,arg):
		"""
		Compares two Period objects to determine if one is less than the other.
		@rtype: boolean
		"""
		if self.__gt__(arg): return False
		if self.__eq__(arg): return False
		return True

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __neq__(self,arg):
		"""
		Compare two Period objects for inequality.
		@rtype: boolean
		"""
		return not self.__eq__(arg)

	#-----------------------------------------------------------------------------------
	#           __str__
	#-----------------------------------------------------------------------------------
	def __str__(self):
		"""
		Returns a string representation of a Period.
		@rtype: string
		@return: a string representation of a Period.
		e.g.::
			"4 days 3 hours 20 minutes 45 seconds"
		"""
		return self.get_p()


	#-----------------------------------------------------------------------------------
	#           __sub__
	#-----------------------------------------------------------------------------------
	def __sub__(self, arg):
		"""
		Subtract one period from another.
		@return: a new Period object
		@rtype: Period
		"""
		if isinstance(arg, Period): pass # no problem
		else:
			raise AssertionError("Cannot subtract a "
				+ arg.__class__.__name__ + " object from a Period object.")

		return Period(0,0,0, self.period_seconds - arg.period_seconds)


	#-----------------------------------------------------------------------------------
	#           subtract
	#-----------------------------------------------------------------------------------
	def subtract(self, **kwargs):
		"""
		A general method for subtracting time from a Period object.
		@rtype: Period

		@note: Example:
		::
			p1 = Period()
			p2 = p1.plus(weeks=2,days=3,hours=4,minutes=99, seconds=1)
		"""
		for key,value in kwargs.items():
			kwargs[key] = value * -1

		return self.add(**kwargs)

	# minus() method is alias for subtract() method
	minus = subtract


	#-----------------------------------------------------------------------------------
	#           add
	#-----------------------------------------------------------------------------------
	def add(self, **kwargs):
		"""
		A general method for adding time to a Period object.  To
		subtract time, add time in negative increments or use the subtract() method.
		@rtype: Period
		@note:
		Example::
			p1 = Period()
			p2 = p1.plus(weeks=2,days=3,hours=4,minutes=99, seconds=1)
		"""
		argNum = 0
		p = self.clone()  # p is a new Period object
		for key, value in kwargs.items():
			argNum += 1
			if False: pass
			elif  key in ("day"    ,"days"   , DAY   , DAYS   ): p = Period(0,0,0,p.period_seconds + (value * SECONDS_IN_DAY   ))
			elif  key in ("hour"   ,"hours"  , HOUR  , HOURS  ): p = Period(0,0,0,p.period_seconds + (value * SECONDS_IN_HOUR  ))
			elif  key in ("minute" ,"minutes", MINUTE, MINUTES): p = Period(0,0,0,p.period_seconds + (value * SECONDS_IN_MINUTE))
			elif  key in ("second" ,"seconds", SECOND, SECONDS): p = Period(0,0,0,p.period_seconds + value )
			elif  key in ("week"   ,"weeks"  , WEEK  , WEEKS  ): p = Period(0,0,0,p.period_seconds + (7*(value * SECONDS_IN_DAY)))
			else :
				raise AssertionError(
				self.__class__.__name__ +".plus()"
				+ " received invalid keyword argument: " + str(key)
				+ " in argument " + str(argNum) + ".\n"
				+ kwargsToString(**kwargs)
				)
		return p

	# plus() method is alias for add() method
	plus = add

	#-----------------------------------------------------------------------------------
	#           clone
	#-----------------------------------------------------------------------------------
	def clone(self):
		"""
		Return a clone of myself.
		@return: a clone of myself
		@rtype: Period
		"""
		return Period(0,0,0,self.period_seconds)

	#-----------------------------------------------------------------------------------
	#           get_days
	#-----------------------------------------------------------------------------------
	def get_days(self):
		"""
		Return the days portion of the period, as an int.
		@rtype: int
		@return: days, e.g.::
			3
		"""
		days, hours, minutes, seconds = self.get_tuple()
		return days
	days = property(get_days)

	#-----------------------------------------------------------------------------------
	#           get_hours
	#-----------------------------------------------------------------------------------
	def get_hours(self):
		"""
		Return the hours portion of the Period, as an int.
		@rtype: int
		@return: hours, e.g.::
			15
		"""
		days, hours, minutes, seconds = self.get_tuple()
		return hours
	hours = property(get_hours)

	#-----------------------------------------------------------------------------------
	#           get_minutes
	#-----------------------------------------------------------------------------------
	def get_minutes(self):
		"""
		Return the minutes portion of the Period, as an int.
		@rtype: int
		@return: minutes, e.g.::
			45
		"""
		days, hours, minutes, seconds = self.get_tuple()
		return minutes
	minutes = property(get_minutes)

	#-----------------------------------------------------------------------------------
	#           get_seconds
	#-----------------------------------------------------------------------------------
	def get_seconds(self):
		"""
		Return the seconds portion of the Period, as an int.
		@rtype: int
		@return: seconds, e.g.::
			45
		"""
		days, hours, minutes, seconds = self.get_tuple()
		return seconds
	seconds = property(get_seconds)

	#-----------------------------------------------------------------------------------
	#           get_p
	#-----------------------------------------------------------------------------------
	def get_p(self, **kwargs):
		"""
		Return myself in a nicely-formatted string.
		@rtype: string
		@return: myself in a nicely-formatted string, e.g.::
			"2 days 3 hours 0 minutes 45 seconds"

		@note:
		::
			if keyword arg showZeroComponents == True:
				all components (days, hours, minutes, seconds) will be shown
			else:
				only non-zero components (except seconds) will be shown

			if the period is empty (has a duration of zero):
				if keyword arg showZeroPeriod == True:
					return "0 seconds"
				else:
					return ""  # the empty string

		"""
		showZeroComponents  = kwargs.get("showZeroComponents",True)
		showZeroPeriod      = kwargs.get("showZeroPeriod",True)

		if self.period_seconds == 0:
			if showZeroPeriod: return "0 " + SECONDS
			else: return ""

		days, hours, minutes, seconds = self.get_tuple()

		if   days == 0   :
			if showZeroComponents  : daysString = "0 " + DAY
			else         : daystring  = ""
		elif days == 1   : daysString = "1 " + DAY
		elif days == -1  : daysString = "-1  " + DAY
		else             : daysString = str(days) + " " + DAYS

		if   hours == 0  :
			if showZeroComponents  : hoursString = "0 " + HOURS
			else         : hoursString = ""
		elif hours == 1  : hoursString = "1 " + HOUR
		elif hours == -1 : hoursString = "-1  " + HOUR
		else             : hoursString = str(hours) + " " + HOURS

		if   minutes == 0:
			if showZeroComponents  : minutesString = "0 " + MINUTES
			else         : minutesString = ""
		elif minutes == 1: minutesString = "1 " + MINUTE
		else             : minutesString = str(minutes) + " " + MINUTES

		if   seconds == 0:
			if showZeroComponents  : secondsString = "0 " + SECONDS
			else         : secondsString = ""
		elif seconds == 1: secondsString = "1 " + SECOND
		elif seconds ==-1: secondsString = "-1  " + SECOND
		else             : secondsString = str(seconds) + " " + SECONDS

		results = ""
		if showZeroComponents:
			results += " " + daysString
			results += " " + hoursString
			results += " " + minutesString
			results += " " + secondsString
		else:
			if days   : results += " " + daysString
			if hours  : results += " " + hoursString
			if minutes: results += " " + minutesString
			if seconds: results += " " + secondsString

		return results.strip()

	p = property(get_p)


	#-----------------------------------------------------------------------------------
	#           get_short
	#-----------------------------------------------------------------------------------
	def get_short(self):
		"""
		Return myself as a nicely formatted string: suppress components whose value is zero.
		@rtype:  string
		@return: myself nicely formatted: suppress components whose value is zero.
		If my duration is zero, return "0 seconds". e.g.::
			"2 days 3 hours"
		@note: This method will never return an empty string.
		If my duration is zero, then it returns the string "0 seconds"
		"""
		return self.get_p(showZeroComponents=False)
	short = property(get_short)

	#-----------------------------------------------------------------------------------
	#           get_shortest
	#-----------------------------------------------------------------------------------
	def get_shortest(self):
		"""
		Return myself as a nicely formatted string: suppress components whose value is zero.
		@rtype:  string
		@return: myself nicely formatted: suppress components whose value is zero.
		e.g.::
			"2 days 3 hours"
		@note: If my duration is 0, this method will return an empty string.
		"""
		return self.get_p(showZeroComponents=False,showZeroPeriod=False)
	shortest = property(get_shortest)

	#-----------------------------------------------------------------------------------
	#           get_timedelta
	#-----------------------------------------------------------------------------------
	def get_timedelta(self):
		"""
		Returns a Period expressed as a datetime.timedelta object
		@return: a Period expressed as a datetime.timedelta object
		@rtype: timedelta
		"""
		days, seconds = divmod(self.period_seconds, SECONDS_IN_DAY)
		return datetime.timedelta(days, seconds)
	timedelta = property(get_timedelta)


	#-----------------------------------------------------------------------------------
	#           get_tuple
	#-----------------------------------------------------------------------------------
	def get_tuple(self):
		"""
		Returns myself formatted as a 4-tuple of ints (days, hours, minutes, seconds).
		@return: myself formatted as a 4-tuple of ints (days, hours, minutes, seconds)
		@rtype: tuple
		"""
		period_seconds = abs(self.period_seconds)

		days   , remainder = divmod(period_seconds, SECONDS_IN_DAY)
		hours  , remainder = divmod(remainder     , SECONDS_IN_HOUR)
		minutes, seconds   = divmod(remainder     , SECONDS_IN_MINUTE)

		if self.period_seconds >= 0:
			return days, hours, minutes, seconds
		else: # self.period_seconds is negative
			return -days, -hours, -minutes, -seconds

	tuple = property(get_tuple)


	#-----------------------------------------------------------------------------------
	#           get_asDays
	#-----------------------------------------------------------------------------------
	def get_asDays(self):
		"""
		Returns this Period, expressed in units of days.
		@return: myself, expressed in units of days
		@rtype:  int
		"""
		days, seconds   = divmod(abs(self.period_seconds), SECONDS_IN_DAY)
		return days
	asDays = property(get_asDays)

	#-----------------------------------------------------------------------------------
	#           get_asHours
	#-----------------------------------------------------------------------------------
	def get_asHours(self):
		"""
		Returns this Period, expressed in units of hours.
		@return: myself, expressed in units of hours
		@rtype:  int
		"""
		hours, seconds   = divmod(abs(self.period_seconds), SECONDS_IN_HOUR)
		return hours
	asHours = property(get_asHours)

	#-----------------------------------------------------------------------------------
	#           get_asMinutes
	#-----------------------------------------------------------------------------------
	def get_asMinutes(self):
		"""
		Returns this Period, expressed in units of minutes.
		@return: myself, expressed in units of minutes
		@rtype:  int
		"""
		minutes, seconds   = divmod(abs(self.period_seconds), SECONDS_IN_MINUTE)
		return minutes
	asMinutes = property(get_asMinutes)

	#-----------------------------------------------------------------------------------
	#           get_asSeconds
	#-----------------------------------------------------------------------------------
	def get_asSeconds(self):
		"""
		Returns this Period, expressed in units of seconds.
		@return: myself, expressed in units of seconds
		@rtype:  int
		"""
		return abs(self.period_seconds)
	asSeconds = property(get_asSeconds)

#-----------------------------------------------------------------------------------
#           end of class definition for Period
#-----------------------------------------------------------------------------------


####################################################################################
####################################################################################
#
#                  class: Time
#
####################################################################################
####################################################################################


class Time:
	"""
	A specific point in time, identified by
	year, month, day, hour, minute, second.

	Python's datetime module calls this a "datetime".
	"""

	#-----------------------------------------------------------------------------------
	#           CONSTRUCTOR
	#-----------------------------------------------------------------------------------
	def __init__(self,arg1=None,month=1,day=1,hour=0,minute=0,second=0):
		"""
		The constructor for a Time object.

		Constructor expects arguments of:
			- None (this will construct a Time object from current date/time) or
			- a datetime.datetime object, or
			- a pyfdate.Time object, or
			- a series of positional arguments: year [,month[,day[,hour[,minute[,second]]]]]
		@rtype: Time
		"""
		if arg1==None:
			# we use the current datetime
			self.datetime = datetime.datetime.now()
			return

		if isinstance(arg1, datetime.datetime):
			# first argument is a datatime.datetime object.
			# Use it, and ignore all other arguments.
			self.datetime = copy.deepcopy(arg1)
			return

		if isinstance(arg1,Time):
			# first argument is a Time object.
			# Use it, and ignore all other arguments.
			self.datetime = copy.deepcopy(arg1.datetime)
			return

		# else...
		year = arg1
		try:
			self.datetime = datetime.datetime(year,month,day,hour,minute,second)
		except ValueError, e:
			raise ValueError(str(e) + "\nArgs to Time.__init__ were:\n"
				+ str(arg1)     + "\n"
				+ str(month)    + "\n"
				+ str(day)      + "\n"
				+ str(hour)     + "\n"
				+ str(minute)   + "\n"
				+ str(second)   + "\n"
				)

	#-----------------------------------------------------------------------------------
	#           __add__
	#-----------------------------------------------------------------------------------
	def __add__(self, arg):
		"""
		Add a Period to this Time to produce a new Time.
		@rtype: Time
		"""
		if isinstance(arg, Period):
			return Time(self.datetime + arg.timedelta)

		raise AssertionError("Cannot add a "
			+ arg.__class__.__name__ + " object to a Time object.")

	#-----------------------------------------------------------------------------------
	#           comparison methods - the basics
	#-----------------------------------------------------------------------------------
	def __eq__(self,arg):
		"""
		Compare two Time objects for equality.
		@rtype: boolean
		"""
		if isinstance(arg, Time): pass # no problem
		else: raise AssertionError("Cannot compare a "
				+ arg.__class__.__name__ + " object to a Time object.")

		if self.datetime == arg.datetime: return True
		return False

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __ge__(self,arg):
		"""
		Compare two Time objects for relative position in time.
		@rtype: boolean
		"""
		if self.__gt__(arg): return True
		if self.__eq__(arg): return True
		return False

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __gt__(self,arg):
		"""
		Compare two Time objects to determine if one is later (greater than) the other.
		@rtype: boolean
		"""
		if isinstance(arg, Time): pass # no problem
		else: raise AssertionError("Cannot compare a "
				+ arg.__class__.__name__ + " object to a Time object.")

		if self.datetime > arg.datetime: return True
		return False

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __le__(self,arg):
		"""
		Compare two Time objects for relative position in time.
		@rtype: boolean
		"""
		if self.__gt__(arg): return False
		return True

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __lt__(self,arg):
		"""
		Compare two Time objects for relative position in time.
		@rtype: boolean
		"""
		if self.__gt__(arg): return False
		if self.__eq__(arg): return False
		return True

	#-----------------------------------------------------------------------------------
	#           comparison method
	#-----------------------------------------------------------------------------------
	def __neq__(self,arg):
		"""
		Compare two Time objects for inequality.
		@rtype: boolean
		"""
		return not self.__eq__(arg)


	#-----------------------------------------------------------------------------------
	#           __str__
	#-----------------------------------------------------------------------------------
	def __str__(self):
		"""
		Return a string representation of self as an isodate + space + isotime
		@rtype: string
		@return: self as an isodate + space + isotime, e.g.::
			"2007-03-02 09:30:45"
		"""
		return self.get_isodatetime(" ")


	#-----------------------------------------------------------------------------------
	#           __sub__
	#-----------------------------------------------------------------------------------
	def __sub__(self, arg):
		"""
		Subtract a Period or a Time from this Time object.

		@rtype: Time or Period
		@return: a Time (if <arg> is a Period) or a Period (if <arg> is a Time)

		@arg  arg: a Period object or a Time object
		@type arg: Period or Time

		@note:
		::
			If <arg> is a Period object:
				Subtract a Period from this Time to produce a new Time,
			else, if <arg> is a Time object:
				Subtract one Time from another Time to produce a Period.

		@note:
		If a Period is returned, it is signed.  That is::
			If an earlier time is subtracted from a later time:
				The Period will be positive
			else:
				the Period will be negative.
		"""
		if isinstance(arg, Time):
			timedelta = self.datetime - arg.datetime
			return Period(timedelta)

		if isinstance(arg, Period):
			return Time(self.datetime - arg.timedelta)

		raise AssertionError("Cannot subtract a "
			+ arg.__class__.__name__ + " object from a Time object.")


	#-----------------------------------------------------------------------------------
	#           add
	#-----------------------------------------------------------------------------------
	def add(self, **kwargs):
		"""
		A method to add time to a Time object.
		This is the basic method for doing date/time arithmetic.

		The units and amounts of time are specified as keyword arguments.

		@rtype: Time
		@return: a new Time object with the specified amounts of time added to it.

		@note: To subtract amounts, you can add negative amounts (see the example)
		or use the 'subtract' method.

		@note: Example: To get the time that is a month and a week from the current time::
			t = Time().add(months=1,weeks=1)
		@note: Example: To get the time that is a month and a week from the current time::
			t = Time().add(months=1).plus(weeks=1)

		@note: Example: To subtract 6 weeks from the current time::
			t = Time().add(weeks=-6)    # note the minus sign: -6.
		"""
		days, hours, minutes, seconds = 0, 0.0, 0.0, 0.0

		t = self.clone()
		p = Period()
		for key, value in kwargs.items():
			if False: pass
			elif  key in ("day"    ,"days"   , DAY   , DAYS   ): p = p.add(days=value)
			elif  key in ("hour"   ,"hours"  , HOUR  , HOURS  ): p = p.add(hours=value)
			elif  key in ("minute" ,"minutes", MINUTE, MINUTES): p = p.add(minutes=value)
			elif  key in ("second" ,"seconds", SECOND, SECONDS): p = p.add(seconds=value)
			elif  key in ("week"   ,"weeks"  , WEEK  , WEEKS  ): p = p.add(weeks=value)
			elif  key in ("month"  ,"months" , MONTH , MONTHS ): t = t.addmonths(value)
			elif  key in ("year"   ,"years"  , YEAR  , YEARS  ): t = t.addmonths(value * 12)
			else:
				raise AssertionError("In Time.plus() method, "
					+ "I do not recognize keyword "
					+ key +" in argment: "
					+ key + "=" + str(value)
					)
		return t + p

	#-----------------------------------------------------------------------------------
	#           plus
	#-----------------------------------------------------------------------------------
	# plus() method is alias for add() method
	plus = add


	#-----------------------------------------------------------------------------------
	#           addmonths
	#-----------------------------------------------------------------------------------
	def addmonths(self, months):
		"""
		A method for adding months to a time object.

		>>> t1 = Time(2004,1,31)
		>>> t1.d
		'January 31, 2004'
		>>> t2 = t1.addmonths(1)
		>>> t2.d
		'February 29, 2004'
		>>> t2 = t1.add(months=8)
		>>> t2.d
		'September 30, 2004'

		@rtype: Time
		@return: a new Time object with the specified amounts of time added to it.

		@note:
		You can use this method directly, e.g.::
			t = Time().addmonths(6)

		Or you can use the standard add() method::
			t = Time().add(months=6)
		"""
		numericMonth = CalendarMonthToNumericMonth(self.year, self.month)
		numericMonth += months
		newYear, newMonth = NumericMonthToCalendarMonth(numericMonth)

		maxDaysInNewMonth = NORMAL_DAYS_IN_MONTH[newMonth]
		if newMonth == 2 and isLeapYear(newYear): maxDaysInNewMonth += 1

		newDay = self.day
		if  self.day > maxDaysInNewMonth:
			# We have moved to a new month that is shorter than the month where we
			# started, and have run off the end of the month.
			# We need to back up to the last day in the new month.
			newDay = maxDaysInNewMonth

		return Time(newYear,newMonth,newDay,self.hour,self.minute,self.second)


	#-----------------------------------------------------------------------------------
	#           anniversary
	#-----------------------------------------------------------------------------------
	def anniversaryOf(self, eventTime):
		"""
		The most recent anniversary of myself.
		@return: The most recent anniversary of some event, previous to today.
		@rtype: Time
		@arg  eventTime: the time of the event whose anniversary we want
		@type eventTime: Time
		@note: In a non-leapyear, the anniversary of an event that occurred
		on February 29 of a leapyear will be moved to February 28.
		"""
		# get eventAnniversaryThisYear
		eventAnniversaryThisYear = eventTime.goto(year=self.year)

		# if the event anniversary has not yet occurred in this year,
		# use the anniversary that occurred last year
		if eventAnniversaryThisYear <= self:
			return eventAnniversaryThisYear
		else:
			return eventTime.goto(year=self.year-1)


	#-----------------------------------------------------------------------------------
	#           clone
	#-----------------------------------------------------------------------------------
	def clone(self, **kwargs):
		"""
		Return a clone of myself.
		@return: a clone of myself
		@rtype: Time

		@note:
		It is possible to change certain parts of the cloned Time
		by using keyword arguments for the component(s) to
		be replaced in the clone.  To make a clone of the current
		time, but one set in the year 1935, for example::
			t1 = Time()
			t2 = t1.clone(year=1935)

		Note that it is possible to trigger a ValueError, if
		for example:
			- The current date is February 29, 2004 (a leap year) and the
			year is reset to 2007 (not a leap year).
			- The current date is January 31 and the month is reset to
			September (which has only 30 days).

		If you *want* to raise a ValueError when such problems occur,
		use the clone() method.  Otherwise, use the goto() method,
		which attempts to recover from such errors::
			t1 = Time()
			t2 = t1.goto(year=1935)
		"""
		year,month,day,hour,minute,second = self.get_tuple()

		for key, value in kwargs.items():
			if value == int(value): pass
			else:
				raise AssertionError("In Time.clone() method, keyword argment: "
					+ key + "=" + str(value)
					+ "\nthe argument value is not an int."
					)

			if False: pass
			elif  key in ("year"   , YEAR  ): year   = value
			elif  key in ("month"  , MONTH ): month  = value
			elif  key in ("day"    , DAY   ): day    = value
			elif  key in ("hour"   , HOUR  ): hour   = value
			elif  key in ("minute" , MINUTE): minute = value
			elif  key in ("second" , SECOND): second = value
			else:
				raise AssertionError("In Time.clone() method, "
					+ "I do not recognize keyword "
					+ key +" in argment: "
					+ key + "=" + str(value)
					)
		return Time(year,month,day,hour,minute,second)


	#-----------------------------------------------------------------------------------
	#           diff
	#-----------------------------------------------------------------------------------
	def diff(self, eventTime):
		"""
		Determine the difference (a Period) between two Times.
		@rtype: Period
		@note:
		Unlike the __sub__ method, the diff (i.e. difference) method
		always returns a Period object with a positive value.
		"""
		if isinstance(eventTime, Time): pass
		else:
			raise AssertionError("Expecting a Time object as argument. Found a "
			+ eventTime.__class__.__name__ + " object.")

		timedelta = self.datetime - eventTime.datetime
		return Period(   abs(timedelta)    )



	#-----------------------------------------------------------------------------------
	#           diffyears
	#-----------------------------------------------------------------------------------
	def diffyears(self, eventTime):
		"""
		Determine the difference (a Period) between myself and the time of some event.
		@rtype: tuple
		@note:
		returns the difference between two Time objects as a tuple of
		(years, Period)
		"""
		if isinstance(eventTime, Time): pass
		else:
			raise AssertionError("Expecting a Time object as argument. Found a "
			+ eventTime.__class__.__name__ + " object.")

		laterTime   = self
		earlierTime = eventTime

		if earlierTime > laterTime:
			laterTime, earlierTime = earlierTime, laterTime

		anniversaryTime = laterTime.anniversaryOf(earlierTime)

		elapsedYears = anniversaryTime.year - earlierTime.year
		periodSinceAnniversary  = laterTime - anniversaryTime

		return elapsedYears, periodSinceAnniversary

	diffy = diffyears


	#-----------------------------------------------------------------------------------
	#           diffyearsmonths
	#-----------------------------------------------------------------------------------
	def diffyearsmonths(self, eventTime):
		"""
		Determine the difference (a Period) between myself and the time of some event.
		@rtype: tuple
		@note:
		returns the difference between two Time objects as a tuple of
		(years,months, Period)
		"""
		if isinstance(eventTime, Time): pass
		else:
			raise AssertionError("Expecting a Time object as argument. Found a "
			+ eventTime.__class__.__name__ + " object.")

		years, days = self.diffmonths(eventTime)
		years, months = divmod(years,12)
		return years, months, days
	diffym = diffyearsmonths

	#-----------------------------------------------------------------------------------
	#           diffmonths
	#-----------------------------------------------------------------------------------
	def diffmonths(self, eventTime):
		"""
		Determine the difference (a Period) between myself and the time of some event.
		@rtype: tuple
		@examle:
		Returns the difference between two Time objects as a tuple of
		(months, Period), so the Period part can be formatted as desired::
			personDateOfBirth = Time(1946,5,8,6,45)
			months, days = Time().diffm(personDateOfBirth)
			print ("He is " + str(months) + " " + str(days) + " old.")

		"""
		if isinstance(eventTime, Time): pass
		else:
			raise AssertionError("Expecting a Time object as argument. Found a "
			+ eventTime.__class__.__name__ + " object.")

		laterTime   = self
		earlierTime = eventTime

		if earlierTime > laterTime:
			laterTime, earlierTime = earlierTime, laterTime

		anniversaryTime = earlierTime.goto(year=laterTime.year,month=laterTime.month)
		# if the event anniversary has not yet occurred in this month,
		# use the anniversary that occurred last year
		if anniversaryTime <= laterTime: pass
		else:
			lastMonth = laterTime.minus(months=1)
			anniversaryTime = earlierTime.goto(year=lastMonth.year,month=lastMonth.month)


		earlierNumericMonth = CalendarMonthToNumericMonth(earlierTime.year, earlierTime.month)
		anniversaryNumericMonth = CalendarMonthToNumericMonth(anniversaryTime.year, anniversaryTime.month)
		elapsedMonths = anniversaryNumericMonth - earlierNumericMonth

		periodSinceAnniversary  = laterTime - anniversaryTime

		return elapsedMonths, periodSinceAnniversary

	diffm = diffmonths


	#-----------------------------------------------------------------------------------
	#           exitWeekend
	#-----------------------------------------------------------------------------------
	def exitWeekend(self, direction=None):
		"""
		return a new Time object which has been moved so it does not fall
		on a Saturday or Sunday.

		@rtype: Time
		@type  direction: string

		@arg direction: the direction in which to exit the weekend::
		@note:
		If the weekday of the current object occurs on the weekend, the
		weekday of the new object is moved out of the weekend::
			if <direction> is NEXT    , the day is moved to the following Monday.
			if <direction> is PREVIOUS, the day is moved to the previous Friday.
			if <direction> is None    , then
				- a Saturday is moved to the previous Friday
				- a Sunday   is moved to the following Monday
		"""
		if self.weekday == 6:  # SATURDAY
			if direction == NEXT: return self.add(days=2)
			return self.add(days=-1)

		elif self.weekday == 7: # SUNDAY
			if direction == PREVIOUS: return self.add(days=-2)
			return self.add(days=1)

		else:
			return self.clone()



	#-----------------------------------------------------------------------------------
	#           flex
	#-----------------------------------------------------------------------------------
	def flex(self, baseTime):
		"""
		A method for adding days to a date, based on a base date.  If the
		day-of-month of my time is less than the day-of-month of the baseTime,
		then calculate the number of days difference and add them to my time.

		This method is designed to be used when doing monthly arithmetic.
		In the following example, we add 1 month to January 31.  Because
		February contains only 28 days, we get February 28.

		If we want to get the counterpart of January 31 in February
		(February 31, which resolves to March 3) we can "flex" the
		date based on the base date of January 31.

		>>> startDate = Time(2003,1,31)
		>>> startDate.d
		'January 31, 2003'
		>>> startDate.add(months=1).d
		'February 28, 2003'
		>>> startDate.add(months=1).flex(startDate).d
		'March 3, 2003'

		@rtype: Time
		@return: a new Time object that has been "flexed" based on the baseTime
		"""
		if baseTime.day > self.day:
			number_of_lost_days = baseTime.day - self.day
			return self.add(days=number_of_lost_days)
		else:
			return self


	#-----------------------------------------------------------------------------------
	#           fromFile
	#-----------------------------------------------------------------------------------
	def fromFile(self, filename):
		"""
		@return: a new Time object with the datetime of the last modification
		date of the file with <filename>.
		@rtype: Time
		@arg filename: a filename
		@type  filename: string
		"""
		timestamp = os.path.getmtime(filename)
		return self.fromTimestamp(timestamp)


	#-----------------------------------------------------------------------------------
	#           fromTimestamp
	#-----------------------------------------------------------------------------------
	def fromTimestamp(self, timestamp):
		"""
		@return: a new Time object with the datetime from <timestamp>.
		@rtype: Time
		@arg timestamp: a timestamp
		@type  timestamp: timestamp
		@see:             the datetime module for documentation
		"""
		return Time(datetime.datetime.fromtimestamp(timestamp))

	#-----------------------------------------------------------------------------------
	#           get_civildate
	#-----------------------------------------------------------------------------------
	def get_civildate(self):
		"""
		Return a string containing the civildate.
		@rtype: string
		@return: the civildate, e.g.::
			"April 30, 2007"
		"""
		return self.get_d()
	civildate = property(get_civildate)

	#-----------------------------------------------------------------------------------
	#           __getCiviltimeBase
	#-----------------------------------------------------------------------------------
	def __getCiviltimeBase(self, **kwargs):
		"""
		A utility method for other civiltime methods.
		@rtype: tuple
		@return: a tuple containing the components of civiltime::
			(hour, minute, second, am_pm_flag)
		"""
		if TimeExpressedIn24Hours:
			return self.hour,self.minute,self.second,""

		# else, fall thru to return time express as am/pm

		am = kwargs.get("am", "am")
		pm = kwargs.get("pm", "pm")

		hour = self.hour
		if   self.hour == 0: hour = 12
		elif self.hour > 12: hour = self.hour -12

		if self.hour < 12: return hour,self.minute,self.second,am
		else:              return hour,self.minute,self.second,pm

	civiltimebase = property(__getCiviltimeBase)


	#-----------------------------------------------------------------------------------
	#           get_civiltime
	#-----------------------------------------------------------------------------------
	def get_civiltime(self, **kwargs):
		"""
		Return a string containing the civil time.

		If keyword arg showseconds=True, time will include seconds.

		If keyword arg showHundredthsOfSeconds=True, time will include hundredths of seconds.

		Note that hundredths of seconds are faked to "00".
		This is primarily for MS-DOS timestamps which show hundredths of seconds,
		even though the clocks of PCs are not accurate to hundredths of seconds.

		@rtype: string
		@return: a string containing the civil time, e.g.::
			"6:30pm"

		@note:
		Civil time as used in United States of America::
			midnight                       = 12:00am
			time between midnight and noon = am
			noon                           = 12:00pm
			time between noon and midnight = am

		@type    showseconds: boolean
		@keyword showseconds: defaults to False.

		@type    showHundredthsOfSeconds: boolean
		@keyword showHundredthsOfSeconds: defaults to False.
		"""
		showseconds = kwargs.get("showseconds", False)
		showHundredthsOfSeconds = kwargs.get("showHundredthsOfSeconds", False)

		if showHundredthsOfSeconds: showseconds = True

		hour, minute,second,ampm = self.__getCiviltimeBase(**kwargs)

		result = str(hour) + CivilTimeSeparator + str(minute).zfill(2)
		if showseconds: result += CivilTimeSeparator + str(second).zfill(2)
		if showHundredthsOfSeconds: result = result + CivilTimeSeparator + "00"

		return result + ampm  # for 24hour time, ampm = ""


	civiltime = property(get_civiltime)
	t = property(get_civiltime)

	#-----------------------------------------------------------------------------------
	#           get_civiltime2
	#-----------------------------------------------------------------------------------
	def get_civiltime2(self):
		"""
		Return a string containing the civil time (including seconds.)
		@rtype: string
		@return: a string containing the civil time including seconds,
		e.g.::
			"6:30:45pm"
		"""
		return self.get_civiltime(showseconds=True)
	civiltime2 = property(get_civiltime2)
	t2         = property(get_civiltime2)

	#-----------------------------------------------------------------------------------
	#           get_d
	#-----------------------------------------------------------------------------------
	def get_d(self):
		"""
		Return a string containing the civildate.
		@rtype: string
		@return: the civildate, e.g.::
			"April 30, 2007"
		"""
		result = []
		for character in CivilDateFormat:
			if   character == "m": result.append(self.monthname)
			elif character == "d": result.append(str(self.day))
			elif character == "y": result.append(str(self.year))
			else                 : result.append(character)
		return "".join(result)

	d  = property(get_d) # d = date = civildate


	#-----------------------------------------------------------------------------------
	#           get_dostime
	#-----------------------------------------------------------------------------------
	def get_dostime(self):
		"""
		Return the datetime in the format used by Microsoft's MS-DOS.
		@rtype: string
		@return: the datetime in the format used by Microsoft's MS-DOS
		"""
		return self.get_civiltime(am="a",pm="p",showHundredthsOfSeconds=True)
	dostime = property(get_dostime)


	#-----------------------------------------------------------------------------------
	#           get_day
	#-----------------------------------------------------------------------------------
	def get_day(self):
		"""
		Return the day part of the datetime.
		@return: day
		@rtype: int
		"""
		return self.datetime.day
	day = property(get_day)


	#-----------------------------------------------------------------------------------
	#           get_dt
	#-----------------------------------------------------------------------------------
	def get_dt(self):
		"""
		Return a string containing the civildate and the time, e.g. "April 30, 2007 6:30pm".
		@rtype: string
		@return: the civildate and the time, e.g.::
			"April 30, 2007 6:30pm"
		"""
		return self.d + " " + self.civiltime
	dt = property(get_dt)  # wdt = weekdayname, date, time

	#-----------------------------------------------------------------------------------
	#           get_dt2
	#-----------------------------------------------------------------------------------
	def get_dt2(self):
		"""
		Return a string containing the civildate and the time (including seconds)
		e.g. "April 30, 2007 6:30:45pm".

		@rtype: string
		@return: the civildate and the time, e.g.::
			"April 30, 2007 6:30:45pm"
		"""
		return self.d + " " + self.civiltime2
	dt2 = property(get_dt2)  # dt = date, time (including seconds)

	#-----------------------------------------------------------------------------------
	#           get_hour
	#-----------------------------------------------------------------------------------
	def get_hour(self):
		"""
		Return the hour portion of the Time, as an int.
		@return: hour
		@rtype: int
		"""
		return self.datetime.hour
	hour = property(get_hour)


	#-----------------------------------------------------------------------------------
	#           get_isodate
	#-----------------------------------------------------------------------------------
	def get_isodate(self,sep="-"):
		"""
		Return a string containing an ISO date in format yyyy-mm-dd, e.g. "2007-10-09"
		@rtype: string
		@return: an ISO date in format yyyy-mm-dd, e.g.::
			"2007-10-09" # Oct 9, 2007

		@type sep: string
		@arg  sep: separator string to use. Defaults to the ISO standard: a dash.
		"""
		return (
				str(self.year).zfill(4)
			+ sep
			+ str(self.month).zfill(2)
			+ sep
			+  str(self.day).zfill(2)
			)
	isodate = property(get_isodate)

	#-----------------------------------------------------------------------------------
	#           get_isotime
	#-----------------------------------------------------------------------------------
	def get_isotime(self,sep=":"):
		"""
		Return a string containing ISO time in format hh:mm:ss, e.g. "11:15:00".
		@rtype: string
		@return: an ISO time in format hh:mm:ss, e.g.::
			"11:15:00"  # 11:15 in the morning

		@type sep: string
		@arg  sep: separator string to use. Defaults to the ISO standard: a colon.
		"""
		return (
				str(self.hour).zfill(2)
			+ sep
			+ str(self.minute).zfill(2)
			+ sep
			+  str(self.second).zfill(2)
			)
	isotime = property(get_isotime)

	#-----------------------------------------------------------------------------------
	#           get_isodatetime
	#-----------------------------------------------------------------------------------
	def get_isodatetime(self,sep="T",datesep="-",timesep=":",seps=None):
		"""
		Return a string containing an ISO datetime in format yyyy-mm-ddThh:mm:ss.
		@rtype: string
		@return: an ISO datetime in format yyyy-mm-ddThh:mm:ss, e.g.::
			"2007-10-09T11:15:00" # Oct 9, 2007 at 11:15 in the morning

		@type sep: string
		@arg  sep: separator string to use between date and time.
		           Default is the ISO standard, a capital letter "T".
		@arg  datesep: separator string to use within date.
		           Default is the ISO standard, a dash "-".
		@arg  timesep: separator string to use within time.
		           Default is the ISO standard, a colon ":".
		@arg  seps: separator string to use within and between date and time.
				If specified, seps over-rides the other separators.
				Note that the value for seps may be a zero-length string.
				"seps" is useful for constructing datetime strings for things like
				datestamps and filenames.
		"""
		if seps != None:
			sep = datesep = timesep = seps
		return self.get_isodate(sep=datesep) + sep + self.get_isotime(sep=timesep)
	isodatetime = property(get_isodatetime)

	#-----------------------------------------------------------------------------------
	#           get_isofilename
	#-----------------------------------------------------------------------------------
	def get_isofilename(self,sep="-"):
		"""
		Return a string containing the ISO datetime in a format suitable for making a filename.
		@rtype: string
		@return: the ISO datetime in a format suitable for making a filename. E.g.::
			"2007-10-09-11-15-00"   # Oct 9, 2007 at 11:15 in the morning

		@note: All parts of the datetime will be separated by dashes.
		@note: A collection of these strings, sorted using a standard string sort,
		will sort in temporal order.

		@type  sep: string
		@arg sep: separator string to use between datetime parts. Default = "-"
		"""
		return self.get_isodate(sep) + sep + self.get_isotime(sep)
	isofilename = property(get_isofilename)


	#-----------------------------------------------------------------------------------
	#           get_isoweekday
	#-----------------------------------------------------------------------------------
	def get_isoweekday(self):
		"""
		Return the ISO weekday number as an int, where Monday=1 .. Sunday=7
		@rtype: int
		@return: the ISO weekday number, e.g.::
			1 # first day of the week, Monday
		"""
		return self.datetime.isoweekday()
	isoweekday = property(get_isoweekday)
	weekday    = property(get_isoweekday)


	#-----------------------------------------------------------------------------------
	#           get_isoweeknumber
	#-----------------------------------------------------------------------------------
	def get_isoweeknumber(self):
		"""
		Return the ISO week number, as an int.
		@rtype: int
		@return: the ISO week number, e.g.::
			1 # first week of the year
		"""
		year, weeknumber, weekday = self.datetime.isocalendar()
		return weeknumber
	weeknumber = property(get_isoweeknumber)
	isoweeknumber = property(get_isoweeknumber)

	#-----------------------------------------------------------------------------------
	#           get_minute
	#-----------------------------------------------------------------------------------
	def get_minute(self):
		"""
		Return the minute portion of a Time, as an int.
		@rtype: int
		@return: minute, e.g.::
			15 # 15 minutes past the beginning of the hour
		"""
		return self.datetime.minute
	minute = property(get_minute)


	#-----------------------------------------------------------------------------------
	#           get_month
	#-----------------------------------------------------------------------------------
	def get_month(self):
		"""
		Return the month portion of a Time, as an int.
		@rtype: int
		@return: month, e.g.::
			12  # for the 12th month, December
		"""
		return self.datetime.month
	month = property(get_month)


	#-----------------------------------------------------------------------------------
	#           get_monthname
	#-----------------------------------------------------------------------------------
	def get_monthname(self):
		"""
		Return a string containing the natural language name of the month.
		@rtype: string
		@return: monthname, e.g.::
			"December"
		"""
		return MONTH_NAMES[self.month]
	monthname = property(get_monthname)
	m         = property(get_monthname)


	#-----------------------------------------------------------------------------------
	#           get_second
	#-----------------------------------------------------------------------------------
	def get_second(self):
		"""
		Return the second portion of a Time, as an int.
		@return: second
		@rtype: int
		"""
		return self.datetime.second
	second = property(get_second)


	#-----------------------------------------------------------------------------------
	#           get_td
	#-----------------------------------------------------------------------------------
	def get_td(self):
		"""
		Return a string containing the time and the civil date.
		@rtype: string
		@return: the time and the civildate, e.g.::
			"6:30pm April 30, 2007"
		"""
		return   self.civiltime + " " + self.d
	td = property(get_td)    # td = time and date



	#-----------------------------------------------------------------------------------
	#           get_t2d
	#-----------------------------------------------------------------------------------
	def get_t2d(self):
		"""
		Return a string containing the time and the civil date
		(including seconds).
		@rtype: string
		@return: the time and the civildate, e.g.::
			"6:30:45pm April 30, 2007"
		"""
		return   self.civiltime2 + " " + self.d
	t2d = property(get_t2d)    # t=time, d=date

	#-----------------------------------------------------------------------------------
	#           get_tuple
	#-----------------------------------------------------------------------------------
	def get_tuple(self):
		"""
		Return a tuple containing the parts of the datetime.
		@rtype: tuple
		@return: myself formatted as a 6-tuple of ints (year, month, day, hour, minute, second).
		E.g.::
			(2007,10,9,11,15,0) # Oct 9, 2007 at 11:15 in the morning
		"""
		return self.year,self.month,self.day,self.hour,self.minute,self.second


	#-----------------------------------------------------------------------------------
	#           get_twd
	#-----------------------------------------------------------------------------------
	def get_twd(self):
		"""
		Return a string containing the time, the weekday name, and the civildate.
		@rtype: string
		@return: the time, the weekday name, and the civildate, e.g.::
			"6:30pm Monday April 30, 2007"
		"""
		return  self.civiltime + " " + self.weekdayname + " " + self.d
	twd = property(get_twd)  # twd = time, weekdayname, and date


	#-----------------------------------------------------------------------------------
	#           get_t2wd
	#-----------------------------------------------------------------------------------
	def get_t2wd(self):
		"""
		Return a string containing the time (including seconds),
		the weekday name, and the civildate.
		@rtype: string
		@return: the time (including seconds), the weekday name, and the civildate, e.g.::
			"6:30:45pm Monday April 30, 2007"
		"""
		return  self.civiltime2 + " " + self.weekdayname + " " + self.d
	t2wd = property(get_t2wd)  # twd = time, weekdayname, and date

	#-----------------------------------------------------------------------------------
	#           get_unixdate
	#-----------------------------------------------------------------------------------
	def get_unixdate(self,sep="-"):
		"""
		Return a string containing a Unix date, e.g. "07-DEC-2006".
		@rtype: string
		@return: a string containing a Unix date, e.g.::
			"07-DEC-2006"

		@type sep: string
		@arg  sep: separator string to use. Defaults to a dash.
		"""
		return (
				str(self.day).zfill(2)
			+ sep
				+ self.monthname.upper()[:3]
			+ sep
			+ str(self.year).zfill(4)
		)
	unixdate = property(get_unixdate)

	#-----------------------------------------------------------------------------------
	#           get_weekdayname
	#-----------------------------------------------------------------------------------
	def get_weekdayname(self, weekday=None):
		"""
		Returns the natural language name of the day of the week.
		@rtype:  string
		@return: the natural language name of the day of the week, e.g.::
			"Monday"

		@type weekday: int
		@arg  weekday: the ISO weekday number. If not specified, defaults
		to the weekday of self (this Time object).
		"""
		if weekday: return WEEKDAY_NAMES[weekday]
		return WEEKDAY_NAMES[self.weekday]

	weekdayname = property(get_weekdayname)
	w           = property(get_weekdayname)


	#-----------------------------------------------------------------------------------
	#           get_wd
	#-----------------------------------------------------------------------------------
	def get_wd(self):
		"""
		Returns a string containing the weekday name and the civildate.
		@rtype: string
		@return: the weekday name and the civildate.
		e.g.::
			"Monday April 30, 2007"
		"""
		return self.weekdayname + " " + self.d
	wd = property(get_wd)  # wd = weekdayname and date


	#-----------------------------------------------------------------------------------
	#           get_wdt
	#-----------------------------------------------------------------------------------
	def get_wdt(self):
		"""
		Returns a string containing the weekday name, the civildate, and the time.
		@rtype: string
		@return: the weekday name, the civildate, and the time, e.g.::
			"Monday April 30, 2007 6:30pm"
		"""
		return self.weekdayname + " " + self.d + " " + self.civiltime
	wdt = property(get_wdt)  # wdt = weekdayname, date, time

	#-----------------------------------------------------------------------------------
	#           get_wdt2
	#-----------------------------------------------------------------------------------
	def get_wdt2(self):
		"""
		Returns a string containing the weekday name, the civildate,
		and the time (including seconds).
		@rtype: string
		@return: the weekday name, the civildate, and the time, e.g.::
			"Monday April 30, 2007 6:30:45pm"
		"""
		return self.weekdayname + " " + self.d + " " + self.civiltime2
	wdt2 = property(get_wdt2)  # w=weekday, d=date, t2=time(including seconds)

	#-----------------------------------------------------------------------------------
	#           get_year
	#-----------------------------------------------------------------------------------
	def get_year(self):
		"""
		Return the year as an int, e.g. 2007
		@rtype: int
		@return: year, e.g.::
			2007
		"""
		return self.datetime.year
	year = property(get_year)


	#-----------------------------------------------------------------------------------
	#           get_yearstring
	#-----------------------------------------------------------------------------------
	def get_yearstring(self):
		"""
		Return the year as a string, e.g. "2007"
		@rtype: string
		@return: year,
		e.g.::
			"2007"
		"""
		return str(self.datetime.year)
	y = property(get_yearstring)



	#-----------------------------------------------------------------------------------
	#           goto
	#-----------------------------------------------------------------------------------
	def goto(self,**kwargs):
		"""
		Returns a clone of self but with some component(s)
		(year, month, day, hour, minute, second) reset to a new value.

		@rtype: Time
		@return: a new Time object in which the time has been moved
		according to the keyword args

		@note:
		A "goto" can fail in a number of ways.
			- The current date is February 29, 2004 (a leap year) and the
			year is reset to 2007 (not a leap year).
			- The current date is January 31 and the month is reset to
			September (which has only 30 days).
		@note: This method attempts to recover from such failures by decrementing
		the "day" value to 28 before failing.

		@note: Example:
		To obtain a Time object whose date is May 15, 2003::
			t  = Time(2007,5,15)
			t2 = t.goto(year=2003)

		@note: Example:
		To obtain a time object whose date is February 28, 2007::
			t  = Time(2004,2,29)      # a leap year
			t2 = t.goto(year=2007)    # not a leap year
		"""
		year  = kwargs.get("year",self.year)
		month = kwargs.get("month",self.month)
		day   = kwargs.get("day",self.day)

		# adjust to normal days in month
		if day > NORMAL_DAYS_IN_MONTH[month]:
			day = NORMAL_DAYS_IN_MONTH[month]

		# possible adjustment to February 29
		possible_day = day
		while month == 2 and (possible_day == 28 or possible_day == 29):
			try:
				return Time(year,month, possible_day
					, kwargs.get("hour",self.hour)
					, kwargs.get("minute",self.minute)
					, kwargs.get("second",self.second)
					)
			except ValueError: pass
			possible_day = possible_day -1

		# fall thru to attempt to do the original move
		return Time(year,month,day
			, kwargs.get("hour",self.hour)
			, kwargs.get("minute",self.minute)
			, kwargs.get("second",self.second)
			)


	#-----------------------------------------------------------------------------------
	#           gotoMonth
	#-----------------------------------------------------------------------------------
	def gotoMonth(self, argMonth, direction=NEXT, **kwargs):
		"""
		Returns a new Time object in which the month has been moved to the specified
		argMonth.

		@rtype: Time
		@return: a new Time object in which the month has been moved to the specified
		month number.

		@type argMonth: int
		@arg  argMonth:
		The argMonth number should be specified by means
		of one of pyfdate's month number constants (JANUARY, FEBRUARY, etc.)

		@type direction: string
		@arg  direction: The direction in time::
			If direction == NEXT    , we will move forward in time to the following month
			If direction == PREVIOUS, we will move backward in time to the preceding month
			If direction == NEAREST , we will move to the nearest month

		@type    useToday: boolean
		@keyword useToday:
		If the current month is the same as argMonth, the value of the
		useToday flag (True or False) will determine whether or not we use
		the current month, or ignore it, in our search for the NEXT, PREVIOUS, or NEAREST month.

		@note: Example:
		If this month is April, to move the date to the following November::
			t = Time().gotoMonth(NOVEMBER)
			or
			t = Time().gotoMonth(NOVEMBER,NEXT)

		@note: Example:
		If this month is April, to move the date to the previous November::
			t = Time().gotoMonth(NOVEMBER, PREVIOUS)


		@note: Example:
		If this month is April, to move the date to the nearest November::
			t = Time().gotoMonth(NOVEMBER, NEAREST)

		@note:
		Question::
			If today is in November and we want to go to the NEXT (or PREVIOUS) November,
			is today considered to be in the next (or previous) November?
		Answer::
			If useToday == True:   (which is the default)
				today is considered to be in the nearest November.
			else:   (useToday=False has been specified as a keyword arg)
				today is ignored in determining the NEXT (or PREVIOUS) November.

		Question::
			If today is November and we want to go to the NEAREST November
			and we have specified useToday=False,
			which is the nearest November: last November or next November?
		Answer::
			NEXT (i.e. the future) November is considered nearest.
		"""
		useToday = kwargs.get("useToday", True)

		if   direction == NEAREST : return self.__gotoNearestMonth(argMonth,useToday)
		elif direction == NEXT    : increment = +1
		elif direction == PREVIOUS: increment = -1
		else:
			raise AssertionError("Invalid argument for direction: " + str(direction))

		m = CalendarMonthToNumericMonth(self.year, self.month)
		newYear, newMonth = NumericMonthToCalendarMonth(m)

		if self.month == argMonth:
			if useToday:
				return self.clone()
			else:
				# ignore today and  move one month in the increment direction
				m += increment
				newYear, newMonth = NumericMonthToCalendarMonth(m)

		while newMonth != argMonth:
				m += increment
				newYear, newMonth = NumericMonthToCalendarMonth(m)

		newTime = Time(newYear, newMonth, self.day, self.hour, self.minute, self.second)
		return newTime

	#-----------------------------------------------------------------------------------
	#           gotoMonthBegin
	#-----------------------------------------------------------------------------------
	def gotoMonthBegin(self):
		"""
		Return a new Time object in which the time has been moved to the beginning of the month.
		@rtype: Time
		@return: a new Time object in which the time has been moved to the beginning of the month.
		@note:
		Example:
		If today is May 15, 2007 then to obtain a time object whose date is May 1::
			t = Time().gotoMonthBegin()
		"""
		return Time(self.year, self.month, 1, self.hour, self.minute, self.second)

	#-----------------------------------------------------------------------------------
	#           gotoMonthEnd
	#-----------------------------------------------------------------------------------
	def gotoMonthEnd(self):
		"""
		Return a new Time object in which the time has been moved to the end of the month.
		@rtype: Time
		@return: a new Time object in which the time has been moved to the end of the month.

		@note: Example:
		If today is May 15, 2007 then to obtain a time object whose date is May 31::
			t = Time().gotoMonthEnd()
		"""
		# we move to the beginning of this month,
		# then add a month so that we're at the beginning of next month,
		# then subtract a day so we're at the end of this month.

		return self.gotoMonthBegin().plus(months=1,days=-1)

	#-----------------------------------------------------------------------------------
	#           gotoYearBegin
	#-----------------------------------------------------------------------------------
	def gotoYearBegin(self):
		"""
		Return a new Time object in which the time has been moved to the beginning of year.
		@rtype: Time
		@return: a new Time object in which the time has been moved to the beginning of year.
		@note: Example:
		If today is May 15, 2007 then to obtain a time object whose date is January 1, 2007::
			t = Time().gotoYearBegin()
		"""
		return Time(self.year, 1,1, self.hour,self.minute,self.second)

	#-----------------------------------------------------------------------------------
	#           gotoYearEnd
	#-----------------------------------------------------------------------------------
	def gotoYearEnd(self):
		"""
		Return a new Time object in which the time has been moved to the end of the year.
		@rtype: Time
		@return: a new Time object in which the time has been moved to the end of the year.
		@note: Example:
		If today is May 15, 2007 then to obtain a time object whose date is December 31, 2007::
			t = Time().gotoYearEnd()
		"""
		# move to January 1 of next year, then backtrack by one day
		return Time(self.year+1, 1,1, self.hour,self.minute,self.second).plus(days=-1)

	#-----------------------------------------------------------------------------------
	#           __gotoNearestMonth
	#-----------------------------------------------------------------------------------
	def __gotoNearestMonth(self, month, useTodayFlag):
		"""
		Return a new Time object in which the month has been moved
		(forward or backward) to the closest month with month number <month>.

		@rtype: Time
		@return:
		a new Time object in which the month has been moved
		(forward or backward) to the closest month with month number <month>.

		@type month: int
		@arg  month: the monthnumber of the the desired month.
		The monthnumber should be specified by means
		of one of pyfdate's month number constants.

		@type useTodayFlag: boolean
		@arg  useTodayFlag: specifies what to do it the current monthnumber is
		the same as the desired monthnumber::
			If useTodayFlag == True:
				return the current month
			else:
				return the month one year in the future.

		@note:
		If  the NEXT     month with monthnumber <month>
		and the PREVIOUS month with monthnumber <month>
		are both exactly six months from the current month,
		then return the NEXT month with monthnumber <month>.

		@note: Example:
			t = Time().__gotoNearestMonth(JULY)
		"""
		if self.month == month:
			if useTodayFlag:
				return self.clone()
			else:
				return self.add(years=1)

		else:
			timeNext = self.gotoMonth(month, NEXT    , useToday=False)
			timePrev = self.gotoMonth(month, PREVIOUS, useToday=False)

			monthnumSelf = CalendarMonthToNumericMonth(self.year, self.month)
			monthnumNext = CalendarMonthToNumericMonth(timeNext.year, timeNext.month)
			monthnumPrev = CalendarMonthToNumericMonth(timePrev.year, timePrev.month)

			futureDifference   = abs(monthnumSelf - monthnumNext)
			pastDifference     = abs(monthnumSelf - monthnumPrev)

			if futureDifference <= pastDifference: return timeNext
			else: return timePrev


	#-----------------------------------------------------------------------------------
	#           __gotoNearestWeekday
	#-----------------------------------------------------------------------------------
	def __gotoNearestWeekday(self, weekday, useTodayFlag):
		"""
		Return a new Time object in which the weekday has been moved
		(forward or backward) to the closest weekday with weekday number <weekday>.

		@note:
		If the current weekday is already <weekday>::
			if useToday == False
				return the NEXT <weekday>
			else
				return a clone of the current Time object.

		@rtype: Time
		@note:
		<weekday> should be specified by means
		of one of pyfdate's weekday number constants.

		@note: Example::
			t = Time().movetoNearestWeekday(THURSDAY)
		"""
		if self.weekday == weekday:
			if useTodayFlag:
				return self.clone()
			else:
				return self.add(weeks=1)

		else:
			futureWeekday = self.gotoWeekday(weekday, NEXT)
			pastWeekday   = self.gotoWeekday(weekday, PREVIOUS)

			futureDifference    = futureWeekday - self
			pastDifference      = self - pastWeekday

			if futureDifference <= pastDifference: return futureWeekday
			else: return pastWeekday

	#-----------------------------------------------------------------------------------
	#           gotoWeekday
	#-----------------------------------------------------------------------------------
	def gotoWeekday(self, argWeekday, direction=NEXT, **kwargs):
		"""
		Return a new Time object in which
		the date has been moved to the specified argWeekday.

		@rtype: Time
		@return: a new Time object in which the time has been moved to the specified weekday.

		@type argWeekday: int
		@arg  argWeekday:
			The argWeekday number should be specified by means
			of one of pyfdate's weekday number constants (MONDAY, TUESDAY, etc.)

		@type direction: string
		@arg  direction: The direction in time::
			If direction == NEXT    , we will move forward in time to the following weekday
			If direction == PREVIOUS, we will move backward in time to the preceding weekday
			If direction == NEAREST , we will move to the nearest weekday

		@type    useToday: boolean
		@keyword useToday:
			If the current weekday is the same as argWeekday, the value of the
			useToday flag (True or False) will determine whether we use the current date,
			or ignore it, in our search for the NEXT, PREVIOUS, or NEAREST weekday.
		"""
		"""

		@note:
		Example:
		If today is Tuesday::
			t = Time().gotoWeekday(THURSDAY)
			or
			t = Time().gotoWeekday(THURSDAY,NEXT)
		will move the date to the following Thursday.

		@note:
		Example:
		If today is Tuesday::
			t = Time().gotoWeekday(THURSDAY, PREVIOUS)
		will move the date to the previous Thursday.

		@note:
		Example:
			t = Time().gotoWeekday(THURSDAY,NEAREST)
		will move the date to the nearest Thursday.

		@note:
		Question: If today is Thursday and we want to go to the NEXT (or PREVIOUS) Thursday:
		Is today considered to be the next (or previous) Thursday?

		Answer::
			If useToday == True:   (which is the default)
				today is considered the nearest Thursday.
			else:   (useToday=False has been specified as a keyword arg)
				today is ignored in determining the NEXT (or PREVIOUS) Thursday.

		Question: if today is Thursday and we want to go to the NEAREST Thursday
		and we have specified useToday=False:
			Which is the nearest Thursday: last Thursday or next Thursday?
		Answer:
			NEXT (i.e. the future) Thursday is considered nearest.
		"""
		useToday = kwargs.get("useToday", True)

		if   direction == NEAREST : return self.__gotoNearestWeekday(argWeekday, useToday)
		elif direction == NEXT    : increment = +1
		elif direction == PREVIOUS: increment = -1
		else:
			raise AssertionError("Invalid argument for direction: " + str(direction))

		if self.weekday == argWeekday:
			if useToday:
				return self.clone()
			else:
				return self.plus(weeks=increment)
		else:
			newTime = self.clone()
			while newTime.weekday != argWeekday:
				newTime = newTime.plus(days=increment)
			return newTime


	#-----------------------------------------------------------------------------------
	#           isLeapYear
	#-----------------------------------------------------------------------------------
	def isLeapYear(self):
		"""
		Return a boolean indicating whether the year is or is not a leap year.

		@return: True if a <year> is a leap year; otherwise return False.
		@rtype: boolean
		"""
		return isLeapYear(self.year)


	#-----------------------------------------------------------------------------------
	#           subtract
	#-----------------------------------------------------------------------------------
	def subtract(self, **kwargs):
		"""
		Subtract some amounts of time from the current time.  Syntactic sugar
		for cases in which you don't want to "add" negative amounts of time.

		@rtype: Time
		@return: a new Time object in which the time has been moved by the specified amounts.

		Coding Example::
			t1 = Time()
			t2 = t1.subtract(weeks=2,days=3,hours=4,minutes=99, seconds=1)
		"""
		for key,value in kwargs.items():
			kwargs[key] = value * -1

		return self.add(**kwargs)

	# minus() method is alias for subtract() method
	minus = subtract
#--------------------------------------------------------------------------------
#    end of definition for Time class
#--------------------------------------------------------------------------------


####################################################################################
####################################################################################
#
#            some useful functions
#
####################################################################################
####################################################################################

#-----------------------------------------------------------------------------
#          argsToString
#-----------------------------------------------------------------------------
def argsToString(*args):
	"""
	A utility routine for showing arguments in error messages.
	Useful for debugging.

	>>> from pyfdate import *
	>>> s = argsToString("test",2,Time())
	>>> print s
	arg     1: "test" <type 'str'>
	arg     2: 2 <type 'int'>
	arg     3: 2008-01-01 14:40:18 <type 'instance'>

	@rtype: string
	"""
	s = ""
	for index, arg in enumerate(args):
		argnum = index + 1
		if type(arg) == type("aaa"): arg = '"%s"' % arg

		s += ("arg " + str(argnum).rjust(5)
				+ ': '
				+ str(arg)
				+ ' '
				+ str(type(arg))
				+ '\n'
				)
	return s

#-----------------------------------------------------------------------------
#          kwargsToString
#-----------------------------------------------------------------------------
def kwargsToString(**kwargs):
	"""
	A utility routine for showing keyword arguments in error messages.
	Useful for debugging.

	>>> from pyfdate import *
	>>> s = kwargsToString(first="test", second=2, third=Time())
	>>> print s
	first     : "test" <type 'str'>
	second    : 2 <type 'int'>
	third     : 2008-01-01 14:36:38 <type 'instance'>

	@rtype: string
	"""
	s = ""
	keys = kwargs.keys()
	keys.sort()

	for key in keys:
		value = kwargs[key]
		if type(value) == type("aaa"): value = '"%s"' % value
		s += (key.ljust(10)
				+ ': '
				+ str(value)
				+ ' '
				+ str(type(value))
				+ '\n')
	return s


#-----------------------------------------------------------------------------------
#           NumericMonthToCalendarMonth
#-----------------------------------------------------------------------------------
def CalendarMonthToNumericMonth(year, month):
	"""
	Convert a calendar month (year,month)
	to a numeric representation:

	>>> CalendarMonthToNumericMonth(2007,4)
	24075

	@rtype: int
	"""
	elapsedYears  = year -1
	elapsedMonths = month -1
	return (elapsedYears * 12) + elapsedMonths

#-----------------------------------------------------------------------------------
#           NumericMonthToCalendarMonth
#-----------------------------------------------------------------------------------
def NumericMonthToCalendarMonth(months):
	"""
	Convert a numeric representation of a month
	to a calendar month (year, month).

	>>> NumericMonthToCalendarMonth(24075)
	(2007, 4)

	@rtype: tuple
	"""
	elapsedYears, elapsedMonths = divmod(months, 12)
	year  = elapsedYears + 1
	month = elapsedMonths + 1
	return year, month


#-----------------------------------------------------------------------------------
#              isLeapYear
#-----------------------------------------------------------------------------------
def isLeapYear(year):
	"""
	Return True if year is a leapyear; otherwise return False.

	>>> isLeapYear(2004)
	True
	>>> isLeapYear(2000)
	True
	>>> isLeapYear(2005)
	False

	@rtype: boolean
	@return: True if year is a leapyear; otherwise return False.
	"""
	try:
		# February 29 is valid only in a leap year
		d = datetime.datetime(year,2,29)
		return True
	except ValueError:
		return False


#-----------------------------------------------------------------------------------
#              to24hour
#-----------------------------------------------------------------------------------
def to24hour(hour, ampm):
	"""
	Convert an hour expressed as am/pm into one expressed in 24 hour time.

	>>> to24hour(12,"am")
	0
	>>> to24hour(1,"am")
	1
	>>> to24hour(12,"PM")
	12
	>>> to24hour(1,"PM")
	13

	@rtype: int
	@return: the number of of an hour in 24-hour (aka "military") time.

	@type hour: int
	@arg  hour: must be an integer (or a string that can be converted to an integer)
	in the range of 1 to 12

	@type ampm: string
	@arg  ampm: must be a string containing either "am" or "pm" (in upper or lower case)
	"""
	try:
		hour = int(hour)
	except:
		raise AssertionError('to24hour() function receives an '
		 + 'invalid value for hour argument: "' + str(hour) + '"')

	ampm = ampm.lower()

	assert hour < 13
	assert hour > 0
	assert ampm in ("am","pm")

	if hour == 12 and ampm == 'am': return 0
	if hour == 12 and ampm == 'pm': return 12
	if ampm == 'pm':  return hour + 12
	return hour

def numsplit(s):
	"""
	split a string into its numeric parts and return
	a list containing the numeric parts converted to ints.

	This function can be used to parse a string containing
	an ISO datetime.

	>>> from pyfdate import *
	>>> numsplit("2007_10_09")
	[2007, 10, 9]
	>>> numsplit("2007-10-09T23:45:59")
	[2007, 10, 9, 23, 45, 59]
	>>> numsplit("2007/10/09 23.45.59")
	[2007, 10, 9, 23, 45, 59]
	"""
	s = list(s)
	for i in range(len(s)):
		if not s[i] in "0123456789": s[i] = " "
	return [int(x) for x in "".join(s).split()]


#--------------------------------------------------------------------------
# test code
#--------------------------------------------------------------------------
if __name__ == "__main__":
	print("pyfdate language is " + LANG)
	t = Time()
	print t.t
	print t.td
	print t.twd

	print t.dt
	print t.dt2

	print t.wdt
	print t.wdt2

	print t.dt + " " + t.w
	print t.dt2 + " " + t.w
	print t.m  + " " + t.y

	for s in (
		"2007_10_09"
		, "2007-10-09T23:45:59"
		, "2007/10/09 23.45.59"
		, "23:45:59"
		):
		print(s.ljust(30)+ " --> " + str(numsplit(s)))

	print "It is now:", t
