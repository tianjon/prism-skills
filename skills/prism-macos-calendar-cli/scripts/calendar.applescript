use framework "Foundation"
use scripting additions

property NSJSONSerialization : a reference to current application's NSJSONSerialization
property NSString : a reference to current application's NSString
property NSData : a reference to current application's NSData
property NSDateFormatter : a reference to current application's NSDateFormatter
property NSTimeZone : a reference to current application's NSTimeZone
property NSLocale : a reference to current application's NSLocale
property NSDate : a reference to current application's NSDate
property NSMutableDictionary : a reference to current application's NSMutableDictionary
property NSMutableArray : a reference to current application's NSMutableArray
property NSNumber : a reference to current application's NSNumber
property NSNull : a reference to current application's NSNull
property NSSortDescriptor : a reference to current application's NSSortDescriptor

on run(argv)
	try
		if (count of argv) < 2 then return my out_error("usage", "missing command. Try: cal --help", missing value, "text")
		
		set group to item 1 of argv
		set action to item 2 of argv
		set opt to my parse_options(argv, 3)
		
		set format to my opt_get(opt, "format", "pretty")
		if (format is not "json") and (format is not "text") and (format is not "pretty") then
			set d to my dict_new()
			my dict_put(d, "format", format as text)
			return my out_error("bad_flag", "invalid --format; expected json|pretty|text", d, "json")
		end if
		
		if group is "doctor" then
			if action is "run" then
				return my doctor_run(opt, format)
			else
				return my out_error("usage", "unknown doctor action: " & action, missing value, format)
			end if
		else if group is "calendars" then
			if action is "list" then
				return my calendars_list(format)
			else
				set d to my dict_new()
				my dict_put(d, "action", action as text)
				return my out_error("usage", "unknown calendars action: " & action, d, format)
			end if
		else if group is "events" then
			if action is "list" then
				return my events_list(opt, format)
			else if action is "search" then
				return my events_search(opt, format)
			else if action is "create" then
				return my events_create(opt, format)
			else if action is "update" then
				return my events_update(opt, format)
			else if action is "delete" then
				return my events_delete(opt, format)
			else
				set d to my dict_new()
				my dict_put(d, "action", action as text)
				return my out_error("usage", "unknown events action: " & action, d, format)
			end if
		else
			set d to my dict_new()
			my dict_put(d, "group", group as text)
			return my out_error("usage", "unknown command group: " & group, d, format)
		end if
	on error errMsg number errNum
		-- Prefer structured errors when format=json. Avoid leaking huge AppleScript traces into stdout.
		set fmt to "text"
		try
			if (count of argv) >= 1 then
				-- best-effort: parse --format if present
				set fmt to my sniff_format(argv)
			end if
		end try
		
		set code to "internal_error"
		set msg to errMsg as text
		if errNum is -1743 then
			set code to "permission_denied"
			set msg to "macOS Automation permission denied. See references/automation-permissions.md. (" & (errMsg as text) & ")"
		else if errNum is -600 then
			set code to "calendar_not_running"
			set msg to "Calendar.app is not running or cannot be launched in this environment. Try opening Calendar.app once, then re-run. (" & (errMsg as text) & ")"
		end if
		
		set d to my dict_new()
		my dict_put(d, "number", errNum as integer)
		return my out_error(code, msg, d, fmt)
	end try
end run

on sniff_format(argv)
	repeat with i from 1 to (count of argv)
		if (item i of argv) is "--format" then
			if i + 1 <= (count of argv) then return item (i + 1) of argv
		end if
	end repeat
	return "pretty"
end sniff_format

on parse_options(argv, start_index)
	set opt to {}
	set i to start_index
	repeat while i <= (count of argv)
		set k to item i of argv
		if k is "--dry-run" then
			set opt to opt & {{"dry_run", "1"}}
			set i to i + 1
		else if k is "--apply" then
			set opt to opt & {{"apply", "1"}}
			set i to i + 1
		else if k begins with "--" then
			if i = (count of argv) then error "flag missing value: " & k
			set v to item (i + 1) of argv
			set opt to opt & {{my strip_prefix(k, "--"), v}}
			set i to i + 2
		else
			error "unexpected arg: " & k
		end if
	end repeat
	return opt
end parse_options

on opt_get(opt, key, default_value)
	repeat with kv in opt
		if (item 1 of kv) is key then return item 2 of kv
	end repeat
	return default_value
end opt_get

on opt_has(opt, key)
	repeat with kv in opt
		if (item 1 of kv) is key then return true
	end repeat
	return false
end opt_has

on strip_prefix(s, prefix)
	if s begins with prefix then
		return text ((length of prefix) + 1) thru -1 of s
	end if
	return s
end strip_prefix

on dict_new()
	return NSMutableDictionary's dictionary()
end dict_new

on arr_new()
	return NSMutableArray's array()
end arr_new

on dict_put(d, k, v)
	if v is missing value then
		d's setObject:(NSNull's null()) forKey:(k as text)
	else
		d's setObject:v forKey:(k as text)
	end if
end dict_put

on join_lines(linesList)
	set outText to ""
	set is_first to true
	repeat with s in linesList
		if is_first then
			set outText to (s as text)
			set is_first to false
		else
			set outText to outText & linefeed & (s as text)
		end if
	end repeat
	return outText
end join_lines

on json_wrap_ok(payload)
	set root to NSMutableDictionary's dictionary()
	root's setObject:(NSNumber's numberWithBool:true) forKey:"ok"
	root's setObject:payload forKey:"data"
	return root
end json_wrap_ok

on json_wrap_err(code, message, details)
	if details is missing value then set details to {}
	set errObj to NSMutableDictionary's dictionary()
	errObj's setObject:(code as text) forKey:"code"
	errObj's setObject:(message as text) forKey:"message"
	errObj's setObject:details forKey:"details"
	
	set root to NSMutableDictionary's dictionary()
	root's setObject:(NSNumber's numberWithBool:false) forKey:"ok"
	root's setObject:errObj forKey:"error"
	return root
end json_wrap_err

on to_json_text(obj, pretty)
	set opts to 0
	if pretty then set opts to (current application's NSJSONWritingPrettyPrinted)

	-- AppleScriptObjC error bridging is unreliable across macOS versions; treat missing result as failure.
	set {theData, theErr} to NSJSONSerialization's dataWithJSONObject:obj options:opts |error|:(reference)
	if theData is missing value then error "failed to serialize JSON"
	
	set theText to (NSString's alloc()'s initWithData:theData encoding:(current application's NSUTF8StringEncoding)) as text
	return theText
end to_json_text

on out_ok(payload, format)
	if format is "json" then
		set obj to my json_wrap_ok(payload)
		set out to my to_json_text(obj, false)
		return out
	else
		return payload as text
	end if
end out_ok

on out_error(code, message, details, format)
	if format is "json" then
		set obj to my json_wrap_err(code, message, details)
		set out to my to_json_text(obj, false)
		return out
	else
		set out to "Error[" & code & "]: " & message
		return out
	end if
end out_error

on ensure_calendar_running()
	-- Launch Calendar without requiring Apple Events first.
	try
		do shell script "/usr/bin/open -a Calendar"
	end try
	
	-- Then wait briefly so subsequent scripting calls do not fail with -600.
	repeat with i from 1 to 20
		try
			tell application "Calendar" to get name
			exit repeat
		on error
			delay 0.1
		end try
	end repeat
end ensure_calendar_running

on calendar_names_array()
	tell application "Calendar"
		set cals to calendars
	end tell
	set namesArr to my arr_new()
	repeat with c in cals
		try
			namesArr's addObject:((name of c) as text)
		end try
	end repeat
	return namesArr
end calendar_names_array

on get_calendar_by_name(calNameText)
	tell application "Calendar"
		set cals to calendars
	end tell
	repeat with c in cals
		try
			if ((name of c) as text) is (calNameText as text) then return c
		end try
	end repeat
	return missing value
end get_calendar_by_name

on doctor_run(opt, format)
	-- Minimal diagnostics for agent/human usage.
	set res to my dict_new()
	my dict_put(res, "osascript", "ok" as text)
	
	my ensure_calendar_running()
	
	tell application "Calendar"
		set calCount to (count of calendars)
	end tell
	my dict_put(res, "calendars_count", calCount as integer)
	
	if format is "json" then return my out_ok(res, "json")
	
	set out_lines to {"Doctor: OK", "calendars: " & (calCount as text), "If you hit permission errors: see references/automation-permissions.md"}
	return my join_lines(out_lines)
end doctor_run

on calendars_list(format)
	my ensure_calendar_running()
	tell application "Calendar"
		set cals to calendars
	end tell
	
	set payload to my arr_new()
	repeat with c in cals
		set calName to ""
		try
			set calName to (name of c) as text
		end try
		set d to my dict_new()
		my dict_put(d, "name", calName as text)
		payload's addObject:d
	end repeat
	
	if format is "json" then
		return my out_ok(payload, "json")
	else
		set out_lines to {}
		set n to (payload's |count|()) as integer
		repeat with i from 0 to (n - 1)
			set itemRec to (payload's objectAtIndex:i)
			set nameText to (itemRec's objectForKey:"name") as text
			if format is "pretty" then
				set idx to (i + 1) as integer
				set out_lines to out_lines & {(idx as text) & ". " & nameText}
			else
				set out_lines to out_lines & {nameText}
			end if
		end repeat
		if (count of out_lines) = 0 then return "(no calendars)"
		return my join_lines(out_lines)
	end if
end calendars_list

on events_payload_to_text(payload)
	-- payload: NSMutableArray of NSDictionary objects
	set out_lines to {"calendar\tstart\tend\ttitle\tid"}
	set n to (payload's |count|()) as integer
	if n = 0 then
		return my join_lines(out_lines)
	end if
	
	repeat with i from 0 to (n - 1)
		set d to (payload's objectAtIndex:i)
		set calName to (d's objectForKey:"calendar") as text
		set startISO to (d's objectForKey:"start") as text
		set endISO to (d's objectForKey:"end") as text
		set titleText to (d's objectForKey:"title") as text
		set idText to (d's objectForKey:"id") as text
		set out_lines to out_lines & {(calName & tab & startISO & tab & endISO & tab & titleText & tab & idText)}
	end repeat
	
	return my join_lines(out_lines)
end events_payload_to_text

on events_payload_to_pretty(payload)
	-- payload: NSMutableArray of NSDictionary objects
	set out_lines to {}
	set n to (payload's |count|()) as integer
	if n = 0 then return "(no events)"
	
	repeat with i from 0 to (n - 1)
		set d to (payload's objectAtIndex:i)
		set calName to (d's objectForKey:"calendar") as text
		set startS to (d's objectForKey:"start_short") as text
		set endS to (d's objectForKey:"end_short") as text
		set titleText to (d's objectForKey:"title") as text
		set idText to (d's objectForKey:"id") as text
		set idx to (i + 1) as integer
		set out_lines to out_lines & {(idx as text) & ". " & startS & "-" & endS & " [" & calName & "] " & titleText & " (id=" & idText & ")"}
	end repeat
	return my join_lines(out_lines)
end events_payload_to_pretty

on finalize_events_payload(payload, opt, format)
	-- Sort by start_ts ascending (if present)
	set n to (payload's |count|()) as integer
	if n > 1 then
		set sortDesc to (NSSortDescriptor's sortDescriptorWithKey:"start_ts" ascending:true)
		payload's sortUsingDescriptors:{sortDesc}
	end if
	
	-- Apply --limit after sorting
	set limitS to my opt_get(opt, "limit", missing value)
	if limitS is not missing value then
		try
			set limitN to (limitS as integer)
			if limitN > 0 then
				repeat while ((payload's |count|()) as integer) > limitN
					payload's removeLastObject()
				end repeat
			end if
		end try
	end if
	
	-- Strip internal keys
	repeat with i from 0 to (((payload's |count|()) as integer) - 1)
		set d to (payload's objectAtIndex:i)
		d's removeObjectForKey:"start_ts"
		if (format is "json") or (format is "text") then
			d's removeObjectForKey:"start_short"
			d's removeObjectForKey:"end_short"
		end if
	end repeat
end finalize_events_payload

on strip_internal_event_keys(d, format)
	if d is missing value then return
	try
		d's removeObjectForKey:"start_ts"
	end try
	if (format is "json") or (format is "text") then
		try
			d's removeObjectForKey:"start_short"
			d's removeObjectForKey:"end_short"
		end try
	end if
end strip_internal_event_keys

on event_record_to_pretty_line(d, prefix)
	set calName to (d's objectForKey:"calendar") as text
	set startS to (d's objectForKey:"start_short") as text
	set endS to (d's objectForKey:"end_short") as text
	set titleText to (d's objectForKey:"title") as text
	set idText to (d's objectForKey:"id") as text
	return (prefix & ": " & startS & "-" & endS & " [" & calName & "] " & titleText & " (id=" & idText & ")")
end event_record_to_pretty_line

on normalize_iso_input(s)
	set t to (s as text)
	set t to my trim_text(t)
	if t contains " " and (t does not contain "T") then
		set AppleScript's text item delimiters to " "
		set parts to text items of t
		set AppleScript's text item delimiters to "T"
		set t to parts as text
		set AppleScript's text item delimiters to ""
	end if
	return t
end normalize_iso_input

on trim_text(t)
	set ns to (current application's NSString's stringWithString:t)
	set ws to current application's NSCharacterSet's whitespaceAndNewlineCharacterSet()
	set trimmed to (ns's stringByTrimmingCharactersInSet:ws) as text
	return trimmed
end trim_text

on parse_date_or_datetime(iso_text, mode)
	-- mode:
	--  - "range_from": date-only allowed -> start of day local
	--  - "range_to": date-only allowed -> next day start local
	--  - "datetime_required": date-only rejected
	set s to my normalize_iso_input(iso_text)
	if (length of s) = 10 then
		if mode is "datetime_required" then error "datetime required, got date-only: " & s
		set df to NSDateFormatter's alloc()'s init()
		df's setLocale:(NSLocale's localeWithLocaleIdentifier:"en_US_POSIX")
		df's setTimeZone:(NSTimeZone's localTimeZone())
		df's setDateFormat:"yyyy-MM-dd"
		set d to (df's dateFromString:s)
		if d is missing value then error "invalid date: " & s
		if mode is "range_to" then
			return (d's dateByAddingTimeInterval:86400) -- next day start
		else
			return d
		end if
	end if
	
	-- Date-time parsing
	set withTZ to false
	if s ends with "Z" then set withTZ to true
	if s contains "+" then set withTZ to true
	-- offset like -07:00 (avoid matching the date part)
	if (offset of "-" in s) > 11 then set withTZ to true
	
	if withTZ then
		-- Let AppleScriptObjC parse ISO8601 with timezone via NSDateFormatter.
		set df2 to NSDateFormatter's alloc()'s init()
		df2's setLocale:(NSLocale's localeWithLocaleIdentifier:"en_US_POSIX")
		df2's setTimeZone:(NSTimeZone's localTimeZone())
		-- Support seconds and optional timezone.
		set candidates to {"yyyy-MM-dd'T'HH:mm:ssXXXXX", "yyyy-MM-dd'T'HH:mmXXXXX"}
		repeat with fmt in candidates
			df2's setDateFormat:fmt
			set d2 to (df2's dateFromString:s)
			if d2 is not missing value then return d2
		end repeat
		error "invalid ISO datetime: " & s
	else
		-- Treat as local time when timezone missing.
		set df3 to NSDateFormatter's alloc()'s init()
		df3's setLocale:(NSLocale's localeWithLocaleIdentifier:"en_US_POSIX")
		df3's setTimeZone:(NSTimeZone's localTimeZone())
		set candidates2 to {"yyyy-MM-dd'T'HH:mm:ss", "yyyy-MM-dd'T'HH:mm"}
		repeat with fmt2 in candidates2
			df3's setDateFormat:fmt2
			set d3 to (df3's dateFromString:s)
			if d3 is not missing value then return d3
		end repeat
		error "invalid local datetime: " & s
	end if
end parse_date_or_datetime

on format_iso_date(d)
	set df to NSDateFormatter's alloc()'s init()
	df's setLocale:(NSLocale's localeWithLocaleIdentifier:"en_US_POSIX")
	df's setTimeZone:(NSTimeZone's localTimeZone())
	df's setDateFormat:"yyyy-MM-dd'T'HH:mm:ssXXXXX"
	return (df's stringFromDate:d) as text
end format_iso_date

on format_short_local(d)
	set df to NSDateFormatter's alloc()'s init()
	df's setLocale:(NSLocale's localeWithLocaleIdentifier:"en_US_POSIX")
	df's setTimeZone:(NSTimeZone's localTimeZone())
	df's setDateFormat:"yyyy-MM-dd HH:mm"
	return (df's stringFromDate:d) as text
end format_short_local

on unix_ts_from_iso(iso_text)
	-- Use Foundation parsing to avoid locale-dependent AppleScript date parsing.
	set s to iso_text as text
	if s is "" then return 0.0
	set df to NSDateFormatter's alloc()'s init()
	df's setLocale:(NSLocale's localeWithLocaleIdentifier:"en_US_POSIX")
	df's setTimeZone:(NSTimeZone's localTimeZone())
	df's setDateFormat:"yyyy-MM-dd'T'HH:mm:ssXXXXX"
	set d to (df's dateFromString:s)
	if d is missing value then return 0.0
	set ts to (d's timeIntervalSince1970()) as real
	return ts
end unix_ts_from_iso

on collect_events_in_range(calObj, fromDate, toDate)
	tell application "Calendar"
		-- Overlap semantics: start < to && end > from
		set evts to (events of calObj whose start date < (toDate as date) and end date > (fromDate as date))
	end tell
	return evts
end collect_events_in_range

on event_to_record(e, calName)
	set evt_title to ""
	set startD to missing value
	set endD to missing value
	set loc to ""
	set notes to ""
	set theURL to ""
	set theUID to ""
	set theID to ""
	
	tell application "Calendar"
		try
			set evt_title to (summary of e) as text
		end try
		try
			set startD to (start date of e)
		end try
		try
			set endD to (end date of e)
		end try
		try
			set vLoc to (location of e)
			if vLoc is missing value then
				set loc to ""
			else
				set loc to vLoc as text
			end if
		end try
		try
			set vDesc to (description of e)
			if vDesc is missing value then
				set notes to ""
			else
				set notes to vDesc as text
			end if
		end try
		try
			set vUrl to (url of e)
			if vUrl is missing value then
				set theURL to ""
			else
				set theURL to vUrl as text
			end if
		end try
		try
			set vUid to (uid of e)
			if vUid is missing value then
				set theUID to ""
			else
				set theUID to vUid as text
			end if
		end try
		try
			set vId to (id of e)
			if vId is missing value then
				set theID to ""
			else
				set theID to vId as text
			end if
		end try
	end tell
	
	set startISO to ""
	set endISO to ""
	set startShort to ""
	set endShort to ""
	set startTsNum to (NSNumber's numberWithDouble:0)
	try
		set startISO to my format_iso_date(startD)
	end try
	try
		set endISO to my format_iso_date(endD)
	end try
	try
		set startShort to my format_short_local(startD)
	end try
	try
		set endShort to my format_short_local(endD)
	end try
	try
		set startTsNum to (NSNumber's numberWithDouble:(my unix_ts_from_iso(startISO)))
	end try

	set d to my dict_new()
	my dict_put(d, "id", theID as text)
	my dict_put(d, "uid", theUID as text)
	my dict_put(d, "calendar", calName as text)
	my dict_put(d, "title", evt_title as text)
	my dict_put(d, "start", startISO as text)
	my dict_put(d, "end", endISO as text)
	my dict_put(d, "start_short", startShort as text)
	my dict_put(d, "end_short", endShort as text)
	my dict_put(d, "start_ts", startTsNum)
	my dict_put(d, "location", loc as text)
	my dict_put(d, "notes", notes as text)
	my dict_put(d, "url", theURL as text)
	return d
end event_to_record

on events_list(opt, format)
	set fromS to my opt_get(opt, "from", missing value)
	set toS to my opt_get(opt, "to", missing value)
	if fromS is missing value or toS is missing value then
		return my out_error("usage", "events list requires --from and --to (or use --range via scripts/cal)", missing value, format)
	end if
	
	set fromDate to my parse_date_or_datetime(fromS, "range_from")
	set toDate to my parse_date_or_datetime(toS, "range_to")
	
	set calNameFilter to my opt_get(opt, "calendar", missing value)
	
	my ensure_calendar_running()
	
	set payload to my arr_new()
	tell application "Calendar"
		set cals to calendars
	end tell
	
	repeat with c in cals
		set calName to ""
		try
			tell application "Calendar" to set calName to (name of c) as text
		end try
		if calNameFilter is missing value or calName is (calNameFilter as text) then
			set evts to my collect_events_in_range(c, fromDate, toDate)
			repeat with e in evts
				payload's addObject:(my event_to_record(e, calName))
			end repeat
		end if
	end repeat

	my finalize_events_payload(payload, opt, format)
	if format is "json" then return my out_ok(payload, "json")
	if format is "pretty" then return my events_payload_to_pretty(payload)
	return my events_payload_to_text(payload)
end events_list

on events_search(opt, format)
	set q to my opt_get(opt, "query", missing value)
	if q is missing value then return my out_error("usage", "events search requires --query", missing value, format)
	
	set fromS to my opt_get(opt, "from", missing value)
	set toS to my opt_get(opt, "to", missing value)
	if fromS is missing value or toS is missing value then
		return my out_error("usage", "events search requires --from and --to (or use --range via scripts/cal)", missing value, format)
	end if
	
	set fromDate to my parse_date_or_datetime(fromS, "range_from")
	set toDate to my parse_date_or_datetime(toS, "range_to")
	set calNameFilter to my opt_get(opt, "calendar", missing value)
	
	my ensure_calendar_running()
	
	set payload to my arr_new()
	tell application "Calendar"
		set cals to calendars
	end tell
	
	repeat with c in cals
		set calName to ""
		try
			tell application "Calendar" to set calName to (name of c) as text
		end try
		if calNameFilter is missing value or calName is (calNameFilter as text) then
			set evts to my collect_events_in_range(c, fromDate, toDate)
			repeat with e in evts
				set titleText to ""
				set notesText to ""
				try
					tell application "Calendar" to set titleText to (summary of e) as text
				end try
				try
					tell application "Calendar" to set notesText to (description of e) as text
				end try
				
				set matched to false
				ignoring case
					if titleText contains (q as text) then set matched to true
					if notesText contains (q as text) then set matched to true
				end ignoring
				
					if matched then payload's addObject:(my event_to_record(e, calName))
				end repeat
			end if
	end repeat

	my finalize_events_payload(payload, opt, format)
	if format is "json" then return my out_ok(payload, "json")
	if format is "pretty" then return my events_payload_to_pretty(payload)
	return my events_payload_to_text(payload)
end events_search

on events_create(opt, format)
	set stage to "init"
	try
		set stage to "read_args"
		set calName to my opt_get(opt, "calendar", missing value)
		set evt_title to my opt_get(opt, "title", missing value)
		set startS to my opt_get(opt, "start", missing value)
		set endS to my opt_get(opt, "end", missing value)
		if calName is missing value or evt_title is missing value or startS is missing value or endS is missing value then
			return my out_error("usage", "events create requires --calendar --title --start --end", missing value, format)
		end if
		
		set stage to "parse_time"
		set startDate to my parse_date_or_datetime(startS, "datetime_required")
		set endDate to my parse_date_or_datetime(endS, "datetime_required")
		
		set loc to my opt_get(opt, "location", "")
		set notes to my opt_get(opt, "notes", "")
		set theURL to my opt_get(opt, "url", "")
		set applyWrite to my opt_has(opt, "apply")
		set dryRun to true
		if applyWrite then set dryRun to false
		if my opt_has(opt, "dry_run") then set dryRun to true
		
		-- basic sanity
		set stage to "validate_time"
		try
			if (endDate as date) <= (startDate as date) then return my out_error("usage", "--end must be after --start", missing value, format)
		end try
		
		set stage to "build_plan"
		set planned to my dict_new()
		my dict_put(planned, "calendar", calName as text)
		my dict_put(planned, "title", evt_title as text)
		my dict_put(planned, "start", my format_iso_date(startDate))
		my dict_put(planned, "end", my format_iso_date(endDate))
		my dict_put(planned, "location", loc as text)
		my dict_put(planned, "notes", notes as text)
		my dict_put(planned, "url", theURL as text)
		my dict_put(planned, "dry_run", (NSNumber's numberWithBool:dryRun))
		if dryRun then
			if format is "json" then return my out_ok(planned, "json")
			return "DRY-RUN: create event '" & (evt_title as text) & "' in calendar '" & (calName as text) & "'"
		end if
		
		set stage to "ensure_running"
		my ensure_calendar_running()
		set stage to "resolve_calendar"
		set calObj to my get_calendar_by_name(calName as text)
		if calObj is missing value then
			set d to my dict_new()
			my dict_put(d, "calendar", calName as text)
			my dict_put(d, "available", my calendar_names_array())
			return my out_error("calendar_not_found", "calendar not found: " & (calName as text), d, format)
		end if
		
		set stage to "make_event:props"
		tell application "Calendar"
			set props to {summary:(evt_title as text), start date:(startDate as date), end date:(endDate as date)}
		end tell
		
		set stage to "make_event:create"
		tell application "Calendar"
			if loc is not "" then set props to props & {location:(loc as text)}
			if notes is not "" then set props to props & {description:(notes as text)}
			if theURL is not "" then set props to props & {url:(theURL as text)}
			set newEvent to make new event at end of events of calObj with properties props
		end tell
		
		-- Return created record
		set stage to "serialize_result"
		set created to my event_to_record(newEvent, calName as text)
		my strip_internal_event_keys(created, format)
		if format is "json" then return my out_ok(created, "json")
		if format is "pretty" then return my event_record_to_pretty_line(created, "CREATED")
		set oneArr to my arr_new()
		oneArr's addObject:created
		return my events_payload_to_text(oneArr)
	on error errMsg number errNum
		set d to my dict_new()
		my dict_put(d, "stage", stage as text)
		my dict_put(d, "number", errNum as integer)
		return my out_error("internal_error", "events create failed at " & stage & ": " & (errMsg as text), d, format)
	end try
end events_create

on resolve_event_by_selector(calObj, selectorKey, selectorVal)
	tell application "Calendar"
		set candidates to {}
		if selectorKey is "id" then
			set candidates to (events of calObj whose id is (selectorVal as text))
		else if selectorKey is "uid" then
			set candidates to (events of calObj whose uid is (selectorVal as text))
		else
			error "unknown selector: " & selectorKey
		end if
	end tell
	return candidates
end resolve_event_by_selector

on find_event(opt, format)
	set idVal to my opt_get(opt, "id", missing value)
	set uidVal to my opt_get(opt, "uid", missing value)
	if idVal is missing value and uidVal is missing value then
		return {ok:false, err:(my out_error("usage", "missing selector: provide --id or --uid", missing value, format))}
	end if
	
	set calNameFilter to my opt_get(opt, "calendar", missing value)
	my ensure_calendar_running()
	
	tell application "Calendar"
		set cals to calendars
	end tell
	
	set found to {}
	set foundCalName to ""
	repeat with c in cals
		set calName to ""
		try
			tell application "Calendar" to set calName to (name of c) as text
		end try
		if calNameFilter is missing value or calName is (calNameFilter as text) then
			set candidates to {}
			if idVal is not missing value then
				set candidates to my resolve_event_by_selector(c, "id", idVal)
			else
				set candidates to my resolve_event_by_selector(c, "uid", uidVal)
			end if
			if (count of candidates) > 0 then
				repeat with e in candidates
					set found to found & {{event:e, calendarName:calName}}
				end repeat
			end if
		end if
	end repeat
	
	if (count of found) = 0 then
		set d to my dict_new()
		if idVal is not missing value then my dict_put(d, "id", idVal as text)
		if uidVal is not missing value then my dict_put(d, "uid", uidVal as text)
		if calNameFilter is not missing value then my dict_put(d, "calendar", calNameFilter as text)
		my dict_put(d, "hint", "Try adding --calendar to narrow scope, or use events search/list to find the event id." as text)
		return {ok:false, err:(my out_error("not_found", "no matching event", d, format))}
	end if
	if (count of found) > 1 then
		-- Return candidates to help the caller disambiguate.
		set payload to my arr_new()
		repeat with itemRec in found
			set e to (event of itemRec)
			set calName to (calendarName of itemRec) as text
			set r to my event_to_record(e, calName)
			my strip_internal_event_keys(r, "json")
			payload's addObject:r
		end repeat
		set d to my dict_new()
		my dict_put(d, "matches", payload)
		my dict_put(d, "hint", "Refine with --calendar, or prefer --id (most deterministic on this machine)." as text)
		return {ok:false, err:(my out_error("ambiguous", "multiple events matched; refine with --calendar or use --id", d, format))}
	end if
	
	set one to item 1 of found
	return {ok:true, event:(event of one), calendarName:(calendarName of one)}
end find_event

on events_update(opt, format)
	set applyWrite to my opt_has(opt, "apply")
	set dryRun to true
	if applyWrite then set dryRun to false
	if my opt_has(opt, "dry_run") then set dryRun to true
	set foundRes to my find_event(opt, format)
	if (ok of foundRes) is false then return (err of foundRes)
	
	set e to (event of foundRes)
	set calName to (calendarName of foundRes) as text
	
	set updates to {}
	if my opt_get(opt, "title", missing value) is not missing value then set updates to updates & {{"title", my opt_get(opt, "title", "")}}
	if my opt_get(opt, "start", missing value) is not missing value then set updates to updates & {{"start", my opt_get(opt, "start", "")}}
	if my opt_get(opt, "end", missing value) is not missing value then set updates to updates & {{"end", my opt_get(opt, "end", "")}}
	if my opt_get(opt, "location", missing value) is not missing value then set updates to updates & {{"location", my opt_get(opt, "location", "")}}
	if my opt_get(opt, "notes", missing value) is not missing value then set updates to updates & {{"notes", my opt_get(opt, "notes", "")}}
	if my opt_get(opt, "url", missing value) is not missing value then set updates to updates & {{"url", my opt_get(opt, "url", "")}}
	
	if (count of updates) = 0 then return my out_error("usage", "no fields to update; provide at least one of --title/--start/--end/--location/--notes/--url", missing value, format)
	
	if dryRun then
		set planned to my dict_new()
		my dict_put(planned, "calendar", calName as text)
		set sel to my dict_new()
		my dict_put(sel, "id", my opt_get(opt, "id", "") as text)
		my dict_put(sel, "uid", my opt_get(opt, "uid", "") as text)
		my dict_put(planned, "selector", sel)
		my dict_put(planned, "updates", updates)
		my dict_put(planned, "dry_run", (NSNumber's numberWithBool:true))
		if format is "json" then return my out_ok(planned, "json")
		return "DRY-RUN: update event in '" & calName & "' (use --apply to write)"
	end if
	
	-- Apply updates
	tell application "Calendar"
		repeat with kv in updates
			set k to item 1 of kv
			set v to item 2 of kv
			if k is "title" then
				set summary of e to (v as text)
			else if k is "start" then
				set start date of e to ((my parse_date_or_datetime(v, "datetime_required")) as date)
			else if k is "end" then
				set end date of e to ((my parse_date_or_datetime(v, "datetime_required")) as date)
			else if k is "location" then
				set location of e to (v as text)
			else if k is "notes" then
				set description of e to (v as text)
			else if k is "url" then
				set url of e to (v as text)
			end if
		end repeat
	end tell
	
	set updated to my event_to_record(e, calName)
	my strip_internal_event_keys(updated, format)
	if format is "json" then return my out_ok(updated, "json")
	if format is "pretty" then return my event_record_to_pretty_line(updated, "UPDATED")
	set oneArr to my arr_new()
	oneArr's addObject:updated
	return my events_payload_to_text(oneArr)
end events_update

on events_delete(opt, format)
	set applyWrite to my opt_has(opt, "apply")
	set dryRun to true
	if applyWrite then set dryRun to false
	if my opt_has(opt, "dry_run") then set dryRun to true
	set foundRes to my find_event(opt, format)
	if (ok of foundRes) is false then return (err of foundRes)
	
	set e to (event of foundRes)
	set calName to (calendarName of foundRes) as text
	
	if dryRun then
		set planned to my dict_new()
		my dict_put(planned, "calendar", calName as text)
		set sel to my dict_new()
		my dict_put(sel, "id", my opt_get(opt, "id", "") as text)
		my dict_put(sel, "uid", my opt_get(opt, "uid", "") as text)
		my dict_put(planned, "selector", sel)
		my dict_put(planned, "dry_run", (NSNumber's numberWithBool:true))
		if format is "json" then return my out_ok(planned, "json")
		return "DRY-RUN: delete event in '" & calName & "' (use --apply to write)"
	end if
	
	tell application "Calendar"
		delete e
	end tell
	
	set res to my dict_new()
	my dict_put(res, "deleted", (NSNumber's numberWithBool:true))
	my dict_put(res, "calendar", calName as text)
	if format is "json" then return my out_ok(res, "json")
	return "DELETED: event in '" & calName & "'"
end events_delete
