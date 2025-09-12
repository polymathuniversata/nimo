;; Nimo Utility Functions
;; This file contains utility functions used throughout the Nimo MeTTa codebase

;; =============================
;; STRING UTILITIES
;; =============================

;; Check if a string starts with a prefix
(= (StartsWith $str $prefix)
   (StringStartsWith $str $prefix))

;; Get string length
(= (StringLength $str)
   (Length $str))

;; Concatenate two strings
(= (ConcatString $str1 $str2)
   (StringConcat $str1 $str2))

;; Concatenate multiple strings
(= (ConcatStrings $str1 $str2 $str3)
   (StringConcat $str1 (StringConcat $str2 $str3)))

(= (ConcatStrings $str1 $str2 $str3 $str4)
   (StringConcat $str1 (StringConcat $str2 (StringConcat $str3 $str4))))

;; Generate a random string
(= (RandomString $length)
   (GenerateRandomString $length))

;; Split string by delimiter
(= (SplitString $text $delimiter)
   (StringSplit $text $delimiter))

;; Count occurrences of substring
(= (CountOccurrences $text $substring)
   (StringCountOccurrences $text $substring))

;; Replace substring in string
(= (ReplaceString $text $old $new)
   (StringReplace $text $old $new))

;; Trim whitespace
(= (TrimString $text)
   (StringTrim $text))

;; Convert to lowercase
(= (ToLowercase $text)
   (StringToLower $text))

;; Convert to uppercase
(= (ToUppercase $text)
   (StringToUpper $text))

;; Hash a string
(= (HashString $text)
   (SHA256Hash $text))

;; =============================
;; LIST UTILITIES
;; =============================

;; Get list length
(= (Length $list)
   (ListLength $list))

;; Check if a list contains an item
(= (Contains $list $item)
   (ListContains $list $item))

;; Append two lists
(= (append $list1 $list2)
   (AppendLists $list1 $list2))

;; Map a function over a list
(= (map $list $function)
   (MapFunction $list $function))

;; Filter a list using a predicate
(= (filter $list $predicate)
   (FilterFunction $list $predicate))

;; Take first N items from a list
(= (TakeN $list $n)
   (TakeNImplementation $list $n))

;; Drop first N items from a list
(= (DropN $list $n)
   (DropNImplementation $list $n))

;; Zip two lists
(= (zip $list1 $list2)
   (ZipLists $list1 $list2))

;; Flatten a list of lists
(= (FlattenLists $lists)
   (FlatMapImplementation $lists Identity))

;; Sort a list
(= (SortList $list)
   (SortListImplementation $list))

;; Sort a list by descending order using a key function
(= (SortByDescending $list $key_function)
   (SortListByDescending $list $key_function))

;; FlatMap function implementation
(= (FlatMap $list $function)
   (FlatMapImplementation $list $function))

;; Left fold over a list
(= (FoldLeft $list $initial $function)
   (FoldLeftImplementation $list $initial $function))

;; Sum a list of numbers
(= (SumList $numbers)
   (FoldLeft $numbers 0 Add))

;; Add function for fold
(= (Add $a $b)
   (+ $a $b))

;; Get first element of pair
(= (First $pair)
   (GetFirst $pair))

;; Get second element of pair
(= (Second $pair)
   (GetSecond $pair))

;; Check if value is a list
(= (IsList $value)
   (IsMeTTaList $value))

;; Execute for each item in a list
(= (foreach $list $function)
   (ForEach $list $function))

;; =============================
;; MATH UTILITIES
;; =============================

;; Max of two values
(= (max $a $b)
   (if (> $a $b) $a $b))

;; Min of two values
(= (min $a $b)
   (if (< $a $b) $a $b))

;; Clamp value between min and max
(= (clamp $value $min $max)
   (min (max $value $min) $max))

;; Calculate percentage
(= (percentage $part $total)
   (if (= $total 0)
       0
       (* (/ $part $total) 100)))

;; Round to decimal places
(= (round $value $decimals)
   (RoundToDecimals $value $decimals))

;; Random number in range
(= (random-range $min $max)
   (RandomInRange $min $max))

;; =============================
;; OBJECT UTILITIES
;; =============================

;; Create a new object
(= (CreateObject)
   (NewObject))

;; Set object property
(= (ObjectSet $obj $key $value)
   (SetObjectProperty $obj $key $value))

;; Get object property
(= (ObjectGet $obj $key)
   (GetObjectProperty $obj $key))

;; Check if object has property
(= (ObjectHasProperty $obj $key)
   (HasObjectProperty $obj $key))

;; Get object keys
(= (ObjectKeys $obj)
   (GetObjectKeys $obj))

;; Convert object to list of pairs
(= (ObjectToPairs $obj)
   (ConvertObjectToPairs $obj))

;; Convert list of pairs to object
(= (PairsToObject $pairs)
   (ConvertPairsToObject $pairs))

;; =============================
;; DATE AND TIME UTILITIES
;; =============================

;; Get current timestamp (Unix epoch seconds)
(= (CurrentTimestamp)
   (GetCurrentUnixTime))

;; Format date
(= (FormatDate $timestamp $format)
   (DateFormat $timestamp $format))

;; Parse date string to timestamp
(= (ParseDate $date_string $format)
   (DateParse $date_string $format))

;; Get today's start timestamp
(= (TodayStartTimestamp)
   (GetTodayStartTime))

;; Add days to timestamp
(= (AddDays $timestamp $days)
   (DateAddDays $timestamp $days))

;; Difference between dates in days
(= (DateDiffDays $timestamp1 $timestamp2)
   (DaysBetween $timestamp1 $timestamp2))

;; =============================
;; NULL CHECKING
;; =============================

;; Check if a value is null
(= (IsNull $value)
   (Equal $value null))

;; Return default if value is null
(= (DefaultIfNull $value $default)
   (if (IsNull $value) $default $value))

;; =============================
;; COMPARISON UTILITIES
;; =============================

;; Check equality
(= (Equal $a $b)
   (EqualityCheck $a $b))

;; =============================
;; LAMBDA FUNCTIONS
;; =============================

;; Create a lambda function
(= (lambda $args $body)
   (Lambda $args $body))

;; Identity function
(= (Identity $x)
   $x)

;; =============================
;; LOGGING UTILITIES
;; =============================

;; Log a message
(= (LogMessage $level $component $message)
   (let (($timestamp (CurrentTimestamp)))
     (Logger $level $component $message $timestamp)))

;; Debug log
(= (LogDebug $component $message)
   (LogMessage "DEBUG" $component $message))

;; Info log
(= (LogInfo $component $message)
   (LogMessage "INFO" $component $message))

;; Warning log
(= (LogWarning $component $message)
   (LogMessage "WARNING" $component $message))

;; Error log
(= (LogError $component $message)
   (LogMessage "ERROR" $component $message))

;; =============================
;; ERROR HANDLING
;; =============================

;; Create an error
(= (Error $message)
   (ErrorResult $message (CurrentTimestamp)))

;; Try to execute an operation with error handling
(= (TryOperation $operation $error_handler)
   (TryCatch $operation $error_handler))

;; =============================
;; EXTERNAL API IMPLEMENTATIONS
;; =============================

;; These would be implemented in the MeTTa runtime

;; String operations
(= (StringStartsWith $str $prefix)
   (ExternalStringStartsWith $str $prefix))

(= (StringConcat $str1 $str2)
   (ExternalStringConcat $str1 $str2))

(= (GenerateRandomString $length)
   (ExternalGenerateRandomString $length))

(= (StringSplit $text $delimiter)
   (ExternalStringSplit $text $delimiter))

(= (StringCountOccurrences $text $substring)
   (ExternalStringCountOccurrences $text $substring))

(= (StringReplace $text $old $new)
   (ExternalStringReplace $text $old $new))

(= (StringTrim $text)
   (ExternalStringTrim $text))

(= (StringToLower $text)
   (ExternalStringToLower $text))

(= (StringToUpper $text)
   (ExternalStringToUpper $text))

(= (SHA256Hash $text)
   (ExternalSHA256Hash $text))

;; List operations
(= (ListLength $list)
   (ExternalListLength $list))

(= (ListContains $list $item)
   (ExternalListContains $list $item))

(= (AppendLists $list1 $list2)
   (ExternalAppendLists $list1 $list2))

(= (MapFunction $list $function)
   (ExternalMapFunction $list $function))

(= (FilterFunction $list $predicate)
   (ExternalFilterFunction $list $predicate))

(= (TakeNImplementation $list $n)
   (ExternalTakeN $list $n))

(= (DropNImplementation $list $n)
   (ExternalDropN $list $n))

(= (ZipLists $list1 $list2)
   (ExternalZipLists $list1 $list2))

(= (FlatMapImplementation $list $function)
   (ExternalFlatMap $list $function))

(= (SortListImplementation $list)
   (ExternalSortList $list))

(= (SortListByDescending $list $key_function)
   (ExternalSortListByDescending $list $key_function))

(= (FoldLeftImplementation $list $initial $function)
   (ExternalFoldLeft $list $initial $function))

(= (GetFirst $pair)
   (ExternalGetFirst $pair))

(= (GetSecond $pair)
   (ExternalGetSecond $pair))

(= (IsMeTTaList $value)
   (ExternalIsList $value))

(= (ForEach $list $function)
   (ExternalForEach $list $function))

;; Math operations
(= (RoundToDecimals $value $decimals)
   (ExternalRoundToDecimals $value $decimals))

(= (RandomInRange $min $max)
   (ExternalRandomInRange $min $max))

;; Object operations
(= (NewObject)
   (ExternalNewObject))

(= (SetObjectProperty $obj $key $value)
   (ExternalSetObjectProperty $obj $key $value))

(= (GetObjectProperty $obj $key)
   (ExternalGetObjectProperty $obj $key))

(= (HasObjectProperty $obj $key)
   (ExternalHasObjectProperty $obj $key))

(= (GetObjectKeys $obj)
   (ExternalGetObjectKeys $obj))

(= (ConvertObjectToPairs $obj)
   (ExternalObjectToPairs $obj))

(= (ConvertPairsToObject $pairs)
   (ExternalPairsToObject $pairs))

;; Date operations
(= (GetCurrentUnixTime)
   (ExternalGetCurrentUnixTime))

(= (DateFormat $timestamp $format)
   (ExternalDateFormat $timestamp $format))

(= (DateParse $date_string $format)
   (ExternalDateParse $date_string $format))

(= (GetTodayStartTime)
   (ExternalGetTodayStartTime))

(= (DateAddDays $timestamp $days)
   (ExternalDateAddDays $timestamp $days))

(= (DaysBetween $timestamp1 $timestamp2)
   (ExternalDaysBetween $timestamp1 $timestamp2))

;; Comparison operations
(= (EqualityCheck $a $b)
   (ExternalEqualityCheck $a $b))

;; Lambda operations
(= (Lambda $args $body)
   (ExternalCreateLambda $args $body))

;; Logging operations
(= (Logger $level $component $message $timestamp)
   (ExternalLogger $level $component $message $timestamp))

;; Error handling
(= (ErrorResult $message $timestamp)
   (ExternalError $message $timestamp))

(= (TryCatch $operation $error_handler)
   (ExternalTryCatch $operation $error_handler))

;; =============================
;; END OF UTILITY FUNCTIONS
;; =============================