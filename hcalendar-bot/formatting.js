exports.FormatDay_v1 = function FormatDay_v1(hDay) {
	return FormatDay(hDay);
}

function FormatDay(hDay)
{
	var hDayStr = hDay + "th";
	if (hDay == 1)
		hDayStr = "1st";
	if (hDay == 2)
		hDayStr = "2nd";
	if (hDay == 3)
		hDayStr = "3rd";
	if (hDay == 21)
		hDayStr = "21st";
	if (hDay == 22)
		hDayStr = "22nd";
	if (hDay == 23)
		hDayStr = "23rd";
	if (hDay == 31)
		hDayStr = "31st";
	if (hDay == 32)
		hDayStr = "32nd";
	if (hDay == 33)
		hDayStr = "33rd";
	if (hDay == 41)
		hDayStr = "41st";
	if (hDay == 42)
		hDayStr = "42nd";
	if (hDay == 43)
		hDayStr = "43rd";
	return hDayStr;
}
