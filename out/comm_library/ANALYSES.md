# The intermediate communication analyses of the 21 library records

## bird_pairs b008 (superhero) -- tie, disputed

**Original:** Who is the dumbest superhero? | Evidence: the dumbest superhero refers to MIN(attribute_value) where attribute_name = 'Intelligence'

**Decision:** How to handle ties at the minimum Intelligence value: return one hero or every hero tied at the minimum

- A (1 rows): Return a single hero with the lowest Intelligence value, picking one arbitrarily if several are tied
- B (3 rows, changes the answer): Return every hero whose Intelligence value equals the minimum Intelligence value

**Reviews:** opus: {'A': 'fits', 'B': 'fits'}; sonnet: {'A': 'does not fit', 'B': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [implied] start from superhero records -- "superhero"
- [implied] link superhero to hero_attribute by hero id (inner join) -- "MIN(attribute_value) where attribute_name = 'Intelligence'"
- [implied] link hero_attribute to attribute by attribute id (inner join) -- "attribute_name = 'Intelligence'"
- [via_evidence] filter attribute_name = 'Intelligence' -- "where attribute_name = 'Intelligence'"
- [via_evidence] rank by attribute_value, lowest first -- "the dumbest superhero refers to MIN(attribute_value)"
- [implied] output superhero_name -- "Who is"
- [implied] return only 1 row -- "the dumbest superhero"
- [left_open] ties at the minimum: pick one arbitrarily -- "Who is the dumbest superhero?"
- [left_open] missing attribute values sort first -- ""

**Open phrase:** "Who is the dumbest superhero? ... MIN(attribute_value)" -- The singular 'Who is ... the dumbest' suggests one answer, but MIN() in the evidence describes a value that several heroes could share, and nothing says how to handle ties.

**Pattern:**
- names the extreme with a singular superlative adjective and states no tie rule
- uses evidence to turn a colloquial trait into an aggregate over a filtered attribute
- leaves the join path through the attribute tables unstated
- implies the output column with 'Who' rather than naming it
- says nothing about missing values in the ranked column

## bird_pairs b015 (superhero) -- tie, mutually recognized

**Original:** Give the hero ID of superhero with the lowest attribute value. | Evidence: lowest attribute value refers to MIN(attribute_value);

**Decision:** How to handle ties for the minimum attribute_value: return every hero that has the minimum value, or just one hero

- A (10 rows): Return the hero IDs of all hero_attribute rows whose attribute_value equals the overall minimum, so every tied hero is included (duplicates are possible when a hero has more than one attribute at the minimum).
- B (1 rows, changes the answer): Return one hero ID with the lowest attribute value, as the singular 'the hero ID' suggests. Ties are broken arbitrarily.
- C0 (7 rows, changes the answer): Return each distinct hero that has the minimum attribute value once, with duplicate hero IDs removed.

**Reviews:** opus: {'B': 'fits', 'A': 'fits', 'C0': 'fits'}; sonnet: {'C0': 'fits', 'A': 'fits', 'B': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [implied] source records are hero-attribute rows (each hero's attribute values) -- "superhero with the lowest attribute value"
- [via_evidence] compute the overall minimum attribute_value across all hero-attribute rows -- "lowest attribute value refers to MIN(attribute_value)"
- [implied] keep rows whose attribute_value equals that minimum -- "with the lowest attribute value"
- [stated] output column: hero_id -- "Give the hero ID"
- [implied] missing attribute values ignored when computing the minimum -- "MIN(attribute_value)"
- [left_open] ties: return every hero whose value equals the minimum -- "the hero ID of superhero"
- [left_open] duplicates: a hero may appear more than once if several of its attributes are at the minimum; no dedup -- ""
- [left_open] no ordering or limit -- ""

**Open phrase:** "Give the hero ID of superhero with the lowest attribute value" -- The singular 'the hero ID' and 'superhero' suggest one answer, but the evidence defines the target as MIN(attribute_value), and matching that value naturally returns every hero that hits it, so a careful reader could reasonably pick either.

**Pattern:**
- names the extreme with a singular superlative ('the lowest') and gives no tie rule
- uses singular nouns for the output, which suggests a single answer
- evidence turns the superlative into an aggregate function but doesn't say whether to filter on it or sort and take the top row
- says nothing about duplicates when one entity has several qualifying records
- names the output column directly

## bird_pairs b029 (thrombosis_prediction) -- which_column_source, mutually recognized

**Original:** How many female patients were given an APS diagnosis? | Evidence: female refers to SEX = 'F'; APS diagnosis refers to Diagnosis='APS'

**Decision:** Which table's Diagnosis column should hold 'APS': the Patient record's diagnosis or the diagnosis recorded on an Examination?

- A (1 rows): Count female patients whose patient-level diagnosis (Patient.Diagnosis) is 'APS'.
- B (1 rows, changes the answer): Count distinct female patients who had at least one examination with the diagnosis 'APS' (Examination.Diagnosis).
- C0 (1 rows): Count distinct female patients with an 'APS' diagnosis in either their Patient record or any Examination record.

**Reviews:** opus: {'C0': 'fits', 'A': 'fits', 'B': 'fits'}; sonnet: {'B': 'fits', 'C0': 'fits', 'A': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [implied] start from patient records -- "How many female patients"
- [via_evidence] filter sex = 'F' -- "female refers to SEX = 'F'"
- [left_open] filter diagnosis = 'APS' on the patient-level Diagnosis column (not the examination one) -- "APS diagnosis refers to Diagnosis='APS'"
- [left_open] no join to other tables -- "were given an APS diagnosis"
- [implied] aggregate all kept records into one row -- "How many"
- [implied] count non-missing patient IDs (no DISTINCT) -- "How many female patients"
- [via_evidence] exact text match, case-sensitive -- "SEX = 'F'; Diagnosis='APS'"

**Open phrase:** "were given an APS diagnosis; Diagnosis='APS'" -- The evidence names a bare column, Diagnosis, without saying which table it belongs to, and 'were given a diagnosis' could mean the patient's recorded primary diagnosis or a diagnosis made at any examination, and both tables have a column with that name.

**Pattern:**
- uses a counting question over an entity noun ('how many ... patients') and gives no rule for distinct counts or duplicates
- moves the filter values into evidence as bare column = value pairs with no table named
- uses an event-like verb phrase ('were given a diagnosis') that could point to a per-event table rather than an attribute of the entity
- does not state that the answer needs only one table, so whether to join is left for the reader to infer

## bird_pairs b031 (thrombosis_prediction) -- counting_unit, disputed

**Original:** What is the percentage of female patient had total protein not within the normal range? | Evidence: female refers to sex = 'F'; total protein not within the normal range refers to TP < '6.0' or TP > '8.5'; calculation = DIVIDE((ID where sex = 'F' and TP < '6.0' or TP > '8.5'), COUNT(ID)) * 100

**Decision:** What to count: lab test records or distinct female patients (a patient with several out-of-range TP results counts once or many times)

- A (1 rows): Among all lab records of female patients, the percentage of records whose total protein is below 6.0 or above 8.5
- B (1 rows, changes the answer): Among female patients who have lab records, the percentage of distinct patients with at least one total protein result below 6.0 or above 8.5
- C0 (1 rows, changes the answer): Among all female patients, including those with no lab records, the percentage of distinct patients with at least one total protein result below 6.0 or above 8.5

**Reviews:** opus: {'B': 'fits', 'C0': 'fits', 'A': 'fits'}; sonnet: {'A': 'does not fit', 'C0': 'does not fit', 'B': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [implied] Link patients to their lab records by patient ID, dropping patients with no lab records -- "female patient had total protein"
- [via_evidence] Keep only female patients (SEX = 'F') -- "female refers to sex = 'F'"
- [via_evidence] Numerator: count joined lab records where the patient is female and TP < 6.0 or TP > 8.5 -- "total protein not within the normal range refers to TP < '6.0' or TP > '8.5'"
- [left_open] Denominator: count all joined lab records of female patients, not all patients -- "COUNT(ID)"
- [left_open] Count lab records rather than distinct patients, so a patient with several records is counted several times -- "percentage of female patient"
- [via_evidence] Compute the result as numerator ÷ denominator × 100 -- "calculation = DIVIDE(..., COUNT(ID)) * 100"
- [contradicted] Group precedence: female AND (TP low OR TP high) -- "sex = 'F' and TP < '6.0' or TP > '8.5'"
- [contradicted] Compare TP as a number (6.0, 8.5), not as text -- "TP < '6.0' or TP > '8.5'"
- [left_open] Missing TP values do not count as abnormal but still count in the denominator -- ""
- [stated] Return one output value, the percentage -- "What is the percentage"

**Open phrase:** "percentage of female patient had total protein not within the normal range" -- The question counts 'patients', which points to distinct people who ever had an abnormal TP, but the evidence's COUNT(ID) over joined rows with no DISTINCT fits counting each lab record, so either reading is reasonable.

**Pattern:**
- Asks for a percentage and names the unit as an entity ('patient'), but the measured attribute sits on a repeated child record
- Evidence gives a pseudo-formula with unscoped COUNT(ID) and never says whether to deduplicate
- Evidence gives numeric thresholds as quoted strings and leaves out the parentheses around the OR condition
- Does not state the denominator; the reader has to infer it is the filtered female population
- Does not say how to handle missing measurement values

## bird_pairs b032 (california_schools) -- missing_values, disputed

**Original:** Please list the phone numbers of the direct charter-funded schools that are opened after 2000/1/1. | Evidence: Charter schools refers to `Charter School (Y/N)` = 1 in the frpm

**Decision:** Whether schools that match the filters but have no phone on record (NULL Phone) should add a NULL entry to the list of phone numbers.

- A (751 rows): Return the Phone value for every directly funded charter school that opened after 2000-01-01, even when that value is missing (NULL).
- B (694 rows, changes the answer): Return only actual phone numbers for directly funded charter schools that opened after 2000-01-01. A missing phone is not a phone number, so it is left out of the list.

**Reviews:** opus: {'B': 'fits', 'A': 'fits'}; sonnet: {'B': 'does not fit', 'A': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [implied] join frpm to schools on CDSCode, dropping unmatched records -- "phone numbers of the ... schools"
- [stated] charter funding type equals 'Directly funded' -- "direct charter-funded"
- [via_evidence] is a charter school (Charter School (Y/N) = 1) -- "Charter schools refers to `Charter School (Y/N)` = 1 in the frpm"
- [stated] OpenDate > '2000-01-01' (strictly after, compared as text) -- "opened after 2000/1/1"
- [stated] output column: Phone -- "list the phone numbers"
- [left_open] keep or drop rows whose Phone is missing -- "list the phone numbers"
- [left_open] no deduplication (one row per matched record) -- "list the phone numbers"
- [implied] no ordering or limit -- "Please list"

**Open phrase:** "list the phone numbers" -- "List the phone numbers" can mean one output row per qualifying school, even when the phone is blank, or it can mean only the phone numbers that actually exist, since a missing value is not a phone number.

**Pattern:**
- uses a compound adjective ('direct charter-funded') to carry two separate filters, with evidence spelling out only one of them
- states a date cutoff with 'after' and a non-standard date format, leaving the reader to map it to a strict comparison
- asks for a single attribute as a plural noun ('phone numbers') and says nothing about missing values
- gives no rule on duplicates, ordering, or limit, so a plain unordered list is assumed
- leaves the table link unstated, relying on the evidence naming the source table

## bird_pairs b034 (california_schools) -- aggregation_level, mutually recognized

**Original:** Which active district has the highest average score in Reading?

**Decision:** Whether to rank districts by one school's AvgScrRead value or by the average of AvgScrRead across each district's schools

- A (1 rows): Among active schools, find the school record with the highest average Reading score and return that school's district
- B (1 rows, changes the answer): Among active schools, group the records by district, average their average Reading scores, and return the district with the highest average
- C0 (1 rows, changes the answer): Use the district-level summary rows in satscores (rtype = 'D'), which already hold each district's average Reading score, and return the active district with the highest one

**Reviews:** opus: {'C0': 'fits', 'A': 'fits', 'B': 'fits'}; sonnet: {'A': 'fits', 'B': 'fits', 'C0': 'does not fit'}

**How the real question carries each requirement of the explicit specification:**

- [implied] start from school records -- "district"
- [implied] link schools to SAT score records on school code (inner join, unmatched dropped) -- "average score in Reading"
- [stated] filter operating status = 'Active' -- "active"
- [stated] output district name only -- "Which ... district"
- [left_open] rank by average SAT reading score column, per school record (no grouping) -- "highest average score in Reading"
- [stated] descending order, keep top 1 -- "highest"
- [implied] missing scores placed last -- "highest"
- [left_open] tie handling: arbitrary single row -- ""
- [implied] duplicates: district may repeat across schools; no dedup needed with limit 1 -- "Which ... district"

**Open phrase:** "Which active district has the highest average score in Reading?" -- "average score" can name the stored per-school column (AvgScrRead), with the district just being where the top school sits, or it can mean a district-level average that asks for aggregation, since the question makes the district the thing being ranked.

**Pattern:**
- makes a higher-level group the subject of the superlative while the ranked value lives on lower-level records
- uses a word ('average') that could name an existing column or ask for an aggregation
- attaches the status filter to the group noun even though it applies to the member records
- names the extreme with a singular superlative and states no tie rule
- leaves the join between entity and score tables unstated, implied by the metric's name

## bird_pairs b041 (california_schools) -- other, mutually recognized

**Original:** What is the average math score of the school with the lowest average score for all subjects, and in which county is it located? | Evidence: Average score for all subjects can be computed by AvgScrMath + AvgScrRead + AvgScrWrite

**Decision:** Whether candidate records are limited to satscores rows that match a school in the schools table (with the county taken from schools.County), or whether every satscores row counts (with the county taken from satscores.cname).

- A (1 rows): Only consider SAT records that link to a school in the schools table. Among those, find the one with the lowest sum of the math, reading and writing averages. Report its math average and the county listed in the schools table.
- B (1 rows, changes the answer): Consider every SAT score record, whether or not it links to the schools table. Find the one with the lowest sum of the math, reading and writing averages. Report its math average and the county name stored in the SAT record itself (cname).
- C0 (1 rows, changes the answer): Take 'school' to mean satscores records marked as school level (rtype = 'S') rather than records that match the schools table. Take the county from satscores.cname.

**Reviews:** opus: {'C0': 'fits', 'A': 'fits', 'B': 'fits'}; sonnet: {'B': 'fits', 'A': 'fits', 'C0': 'does not fit'}

**How the real question carries each requirement of the explicit specification:**

- [implied] start from SAT score records -- "average math score of the school"
- [left_open] link SAT records to schools by CDS code, inner join (drop unmatched) -- "in which county is it located"
- [left_open] exclude records with missing math average -- ""
- [via_evidence] rank by sum of math + reading + writing averages -- "Average score for all subjects can be computed by AvgScrMath + AvgScrRead + AvgScrWrite"
- [stated] ascending order, take the lowest -- "the school with the lowest average score for all subjects"
- [left_open] missing sums sort first / null handling in ordering -- ""
- [stated] output math average -- "What is the average math score"
- [left_open] output county from schools table -- "in which county is it located"
- [implied] limit to 1 row (no tie handling) -- "the school with the lowest"

**Open phrase:** "in which county is it located" -- The SAT records already hold a county name, so a reader can answer the question from that table alone, but "located" could also mean looking up the school's official location in the schools table, which drops SAT records that have no matching school.

**Pattern:**
- names the extreme with a singular superlative ("the lowest") and states no tie rule
- defines the ranking quantity in the evidence as a sum of columns while the question calls it an "average"
- asks for a location attribute without saying which source table it comes from
- says nothing about missing values in the ranked or reported columns
- combines two requested outputs in one sentence (a metric and a location) about the same single entity

## batch1 b005 (california_schools) -- output_form, mutually recognized

**Original:** If there are any, what are the websites address of the schools with a free meal count of 1,900-2,000 to students aged 5-17? Include the name of the school.

**Decision:** The order of the output columns: website first and school name second, or school name first and website second.

- A (2 rows): List each matching school's website address first, then its name (website, school name), for schools whose free meal count for ages 5-17 is between 1,900 and 2,000 and that have a website.
- B (2 rows, changes the answer): List each matching school's name first, then its website address (school name, website), for schools whose free meal count for ages 5-17 is between 1,900 and 2,000 and that have a website.

**Reviews:** opus: {'B': 'fits', 'A': 'fits'}; sonnet: {'A': 'fits', 'B': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [implied] one row per free-meal record, linked to its school directory record by school code; records with no match are dropped -- "the schools with a free meal count"
- [stated] free meal count for ages 5-17 is between 1900 and 2000, inclusive -- "free meal count of 1,900-2,000 to students aged 5-17"
- [implied] exclude schools whose website is missing -- "If there are any, what are the websites address"
- [stated] output website address -- "what are the websites address"
- [stated] output school name -- "Include the name of the school"
- [left_open] column order: website first, then school name -- "what are the websites address ... Include the name of the school"
- [implied] no ordering, limit, deduplication or tie handling -- ""

**Open phrase:** "what are the websites address of the schools ... Include the name of the school." -- The website is what the question asks for, so it could come first, but 'Include the name of the school' adds the name as an identifying label, and labels usually come first. The wording doesn't fix the position.

**Pattern:**
- asks for one attribute and adds a second output column in a separate 'include' sentence, without saying which column comes first
- gives a numeric range with a hyphen and leaves the reader to assume the ends are included
- uses 'if there are any' to hint that rows without the requested value should be left out, rather than stating a missing-value filter
- leaves the link between the two record sources unstated and lets it follow from the phrase 'schools with'
- names the measure with its age qualifier in everyday words ('to students aged 5-17')

## batch1 b008 (california_schools) -- output_form, mutually recognized

**Original:** Which different county has the most number of closed schools? Please provide the name of each school as well as the closure date. | Evidence: Closure date and closed date are synonyms; 'Closed' was mentioned in schools.StatusType.

**Decision:** Which columns the answer returns: whether the county name is included next to each closed school's name and closure date, or only the school name and closure date are returned.

- A (858 rows): Return the county with the most closed schools as a column, alongside each of its closed schools' names and closure dates. 'Which county' is treated as part of the requested output.
- B (858 rows, changes the answer): Use the county only to choose which schools to list. Return just each closed school's name and closure date, since the question says 'Please provide the name of each school as well as the closure date'.
- C0 (867 rows, changes the answer): Return the county, school name and closure date for every closed school record in the top county, with no de-duplication of repeated name/date pairs.
- C1 (867 rows, changes the answer): Return only the school name and closure date for every closed school record in the top county, with no de-duplication of repeated name/date pairs.

**Reviews:** opus: {'A': 'fits', 'C1': 'fits', 'B': 'fits', 'C0': 'fits'}; sonnet: {'C0': 'does not fit', 'C1': 'fits', 'A': 'fits', 'B': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [via_evidence] restrict to closed schools (StatusType = 'Closed') -- "closed schools; 'Closed' was mentioned in schools.StatusType"
- [implied] group closed schools by county and count them -- "Which different county has the most number of closed schools"
- [left_open] count only records with a non-missing school name (COUNT(School)) -- ""
- [stated] pick the single county with the highest count (limit 1) -- "the most number of"
- [left_open] tie rule among counties with equal max count -- ""
- [implied] list records in that county that are closed -- "the name of each school"
- [left_open] exclude records with missing school name -- ""
- [left_open] output county name -- "Which different county"
- [stated] output school name -- "the name of each school"
- [via_evidence] output closure date (ClosedDate) -- "as well as the closure date; Closure date and closed date are synonyms"
- [left_open] remove duplicate result rows -- ""
- [implied] no ordering of output rows -- ""

**Open phrase:** "Which different county has the most number of closed schools? Please provide the name of each school as well as the closure date." -- The first sentence asks 'which county', so it reads like part of the answer. But the second sentence lists exactly what to provide (school name and closure date), so the county could just be the filter that picks which schools to list.

**Pattern:**
- asks for an argmax entity in a question sentence and then gives a separate explicit list of output fields that leaves that entity out
- names the extreme with a singular superlative and states no tie rule
- relies on evidence to map a status word to a column value and to link a synonym to a column name
- leaves the handling of missing names and duplicate rows unstated
- uses the loose phrase 'different county', which implies grouping by county without stating it

## batch1 b011 (california_schools) -- which_column_source, disputed

**Original:** What is the administrator's email address for the school with the highest number of test takers who received SAT scores of at least 1500?Provide the name of the school.

**Decision:** Where the school name comes from when the top row is Los Angeles Unified's district-level record, whose schools.School is NULL. The gold returns schools.School unchanged (NULL). The agent filled in a name from satscores.sname or from the district name.

- A (1 rows): Return the administrator email and the value of schools.School for the row with the highest NumGE1500, even if that value is NULL.
- B (1 rows, changes the answer): Return the administrator email and a name for the top-ranked entity. Use the SAT table's school name if there is one, otherwise schools.School, otherwise the district name, because the top record is a district-level record with no school name.
- C0 (1 rows, changes the answer): Only real schools count, so district-level records are excluded and the answer is the school-level record with the highest NumGE1500.
- C1 (1 rows): Take the school name from the SAT scores table (satscores.sname) instead of the schools table.

**Reviews:** opus: {'C0': 'fits', 'B': 'fits', 'C1': 'fits', 'A': 'fits'}; sonnet: {'C0': 'fits', 'C1': 'fits', 'A': 'fits', 'B': 'does not fit'}

**How the real question carries each requirement of the explicit specification:**

- [implied] start from SAT score records per school -- "the school with the highest number of test takers who received SAT scores"
- [implied] link SAT records to schools by CDS code, inner join (unmatched dropped) -- "administrator's email address for the school"
- [stated] rank by number of test takers scoring >= 1500 (NumGE1500) -- "highest number of test takers who received SAT scores of at least 1500"
- [stated] descending order, keep top 1 -- "the school with the highest"
- [implied] missing counts placed last -- "highest number"
- [stated] output column 1: primary administrator email (AdmEmail1) -- "administrator's email address"
- [stated] output column 2: school name from schools.School -- "Provide the name of the school."
- [implied] which administrator email field if there are several (the first one) -- "the administrator's email address"
- [left_open] tie rule for the top value -- "the school with the highest"
- [left_open] handling of a NULL school name on the top record -- "Provide the name of the school."

**Open phrase:** "Provide the name of the school." -- "The name of the school" can mean the School column of the matched schools record, even if it is empty, or any available name for the top entity. A reader who sees a district-level record with no school name could reasonably use the SAT table's name or the district name as a fallback.

**Pattern:**
- names the ranking metric in natural language that closely matches a single numeric column
- picks one entity with a singular superlative and gives no tie rule
- adds the requested output fields as a separate trailing imperative sentence
- says 'school' for records that may actually be district-level, without covering that case
- does not say where the name comes from when more than one table has a name field
- leaves missing values unaddressed for both the ranking metric and the output name

## batch1 b012 (financial) -- time_scope, disputed

**Original:** For the client who applied the biggest loan, what was his/her first amount of transaction after opened the account?

**Decision:** Whether a transaction on the account-opening date counts as 'after opened the account' (inclusive vs. strictly later boundary)

- A (1 rows): Take the account with the biggest loan and return the amount of its earliest transaction, including any transaction made on the day the account was opened.
- B (1 rows, changes the answer): Take the account with the biggest loan and return the amount of its earliest transaction made strictly after the opening date, so transactions on the opening day are excluded.

**Reviews:** opus: {'A': 'fits', 'B': 'fits'}; sonnet: {'B': 'does not fit', 'A': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [stated] start from loan records -- "the client who applied the biggest loan"
- [implied] link loan to its account via account_id (inner join) -- "his/her ... after opened the account"
- [implied] link account to its transactions via account_id (inner join) -- "his/her first amount of transaction"
- [stated] pick the biggest loan by loan principal amount, descending -- "the biggest loan"
- [stated] within that loan's account, the earliest transaction by date ascending -- "first amount of transaction"
- [contradicted] no filter restricting transactions relative to the account opening date -- "after opened the account"
- [stated] output column: transaction amount -- "amount of transaction"
- [implied] limit to a single row -- "the client ... his/her first amount"
- [left_open] ties on biggest loan amount or on the earliest date -- ""
- [left_open] missing loan amounts or dates ordering -- ""
- [implied] path through client/disposition tables not required; the account stands in for the client -- "the client who applied the biggest loan"

**Open phrase:** "first amount of transaction after opened the account" -- "after opened the account" can be read loosely as "once the account existed", so the very first transaction counts, including one on the opening day, or strictly as a date filter trans.date > account.date that drops opening-day transactions.

**Pattern:**
- names the target entity through a singular superlative on a related record and states no tie rule
- uses 'first' to mean earliest by date without naming the date column
- adds a temporal clause ('after' an event) that may only describe the setting but reads like a filter
- refers to a person while the query actually works at the account level, leaving the join path implied
- gives no evidence text, so column meanings and the ordering direction rest on ordinary wording

## batch1 b017 (financial) -- counting_unit, disputed

**Original:** What is the average number of crimes committed in 1995 in regions where the number exceeds 4000 and the region has accounts that are opened starting from the year 1997? | Evidence: A3 refers to region names; A15 stands for the average number of crimes commited in 1995.

**Decision:** Counting unit for the average: whether each qualifying district's 1995 crime count (A15) is counted once per qualifying account (joined rows) or once per district.

- A (1 rows): Join districts to their accounts opened in 1997 or later, keep rows where the district's 1995 crimes exceed 4000, and average A15 over those joined rows. A district with many such accounts counts many times.
- B (1 rows, changes the answer): Take each district once. Keep it if its 1995 crimes exceed 4000 and it has at least one account opened in 1997 or later, then average A15 over those districts.
- C0 (1 rows, changes the answer): Take each district once. Keep it if its 1995 crimes exceed 4000 and its region (A3) has at least one account opened in 1997 or later, possibly in a different district of that region. Then average A15 over those districts. This is the agent's region-level match.

**Reviews:** opus: {'C0': 'fits', 'A': 'fits', 'B': 'fits'}; sonnet: {'C0': 'does not fit', 'A': 'does not fit', 'B': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [stated] start from district records (regions) -- "in regions"
- [implied] link district to account by district_id -- "the region has accounts"
- [implied] inner join: drop districts with no matching account -- "the region has accounts that are opened"
- [stated] filter account opening year >= 1997 (text comparison of year) -- "opened starting from the year 1997"
- [stated] filter district.A15 > 4000 -- "where the number exceeds 4000"
- [via_evidence] A15 is the 1995 crime count column -- "A15 stands for the average number of crimes commited in 1995"
- [implied] all kept rows form one group, one result row -- "What is the average number"
- [stated] output AVG(A15) -- "average number of crimes committed in 1995"
- [left_open] average over joined rows (a district is counted once per qualifying account) -- "in regions where ... the region has accounts"
- [left_open] missing A15 values ignored; result missing if none -- ""

**Open phrase:** "None" -- None

**Pattern:**

## batch1 b024 (toxicology) -- output_form, disputed

**Original:** What is the most common bond type? | Evidence: most common bond type refers MAX(COUNT(bond_type))

**Decision:** Whether the output should be only the bond type, or the bond type together with how many times it occurs

- A (1 rows): Return only the most frequent bond_type value.
- B (1 rows, changes the answer): Return the most frequent bond_type value along with its bond count as supporting evidence.

**Reviews:** opus: {'A': 'fits', 'B': 'fits'}; sonnet: {'B': 'does not fit', 'A': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [implied] source records: every bond record -- "bond type"
- [via_evidence] group by bond_type -- "COUNT(bond_type)"
- [via_evidence] count bonds per type (COUNT of bond_id, non-null) -- "most common bond type refers MAX(COUNT(bond_type))"
- [stated] order by count descending -- "most common"
- [implied] keep only the top 1 row -- "the most common bond type"
- [left_open] tie handling: arbitrary single row -- ""
- [left_open] missing bond_type treated as its own group -- ""
- [implied] output column: bond_type only -- "What is the most common bond type?"
- [left_open] count not included in final output -- ""

**Open phrase:** "What is the most common bond type?" -- The question asks 'what is' the type, which suggests just the value, but the evidence names MAX(COUNT(...)) as the thing that defines the answer, so a reader could also return that count as support.

**Pattern:**
- asks for a single entity using a singular superlative ('most common') and gives no tie rule
- relies on evidence to turn 'common' into a grouped count and a max
- states the output only through the 'what is X' wording and doesn't say whether the aggregate that ranks the rows should be shown
- says nothing about null categories or which column is counted

## batch1 b025 (toxicology) -- output_form, mutually recognized

**Original:** What is the percentage of carbon in double-bond molecules? | Evidence: carbon refers to element = 'c'; double-bond molecules refers to bond_type = '='; percentage = DIVIDE(SUM(element = 'c'), COUNT(atom_id))

**Decision:** Order of the arithmetic in the percentage: the gold multiplies the carbon count by 100 and then divides by the total atom count. The agent divides first and then multiplies by 100. The question and evidence only give DIVIDE(SUM(element='c'), COUNT(atom_id)) and do not fix the order. The atom population is the same in both: distinct atoms in molecules that have at least one '=' bond. The two results differ only in the last floating-point digit (38.698505286183014 vs 38.69850528618301).

- A (1 rows): Among all distinct atoms in molecules that contain a double bond, the share that are carbon, computed as carbon count × 100 / total atom count.
- B (1 rows, changes the answer): The same share over the same atoms, computed as (carbon count / total atom count) × 100. The value is the same up to floating-point rounding in the last digit.

**Reviews:** opus: {'B': 'fits', 'A': 'fits'}; sonnet: {'B': 'fits', 'A': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [implied] start from atom records -- "percentage of carbon"
- [implied] link atoms to bonds by molecule id -- "in double-bond molecules"
- [via_evidence] keep only bonds whose type is '=' -- "double-bond molecules refers to bond_type = '='"
- [via_evidence] carbon means element = 'c' -- "carbon refers to element = 'c'"
- [implied] one overall result row (no grouping) -- "What is the percentage"
- [left_open] count distinct carbon atom ids (dedupe join fan-out) -- "SUM(element = 'c')"
- [left_open] denominator is distinct atom ids -- "COUNT(atom_id)"
- [implied] multiply by 100 to express as a percentage -- "percentage"
- [left_open] order of operations: (A × 100) ÷ B -- "percentage = DIVIDE(SUM(element = 'c'), COUNT(atom_id))"
- [implied] single output column holding the percentage -- "What is the percentage of carbon"

**Open phrase:** "percentage = DIVIDE(SUM(element = 'c'), COUNT(atom_id))" -- The evidence gives only a ratio and the word 'percentage' implies ×100 without saying where it goes, and the two placements are the same mathematically, differing only in floating-point rounding.

**Pattern:**
- names the target quantity as a 'percentage' but its evidence formula gives only a bare ratio, leaving the ×100 scaling and where it goes unstated
- defines the subgroup ('double-bond molecules') through a property of a related entity, so the link between records is implied
- puts domain terms into column values through evidence mappings
- writes the formula as SUM/COUNT and says nothing about removing duplicates that the join creates
- asks for one overall figure with no grouping, ordering, or tie concerns

## batch1 b028 (toxicology) -- output_form, mutually recognized

**Original:** How many atoms with iodine and with sulfur type elements are there in single bond molecules? | Evidence: with iodine element refer to element = 'i'; with sulfur element refers to element = 's'; single type bond refers to bond_type = '-'; Should consider the distinct atoms when counting;

**Decision:** Whether to report the iodine and sulfur atom counts separately (one count per element) or as one combined total of atoms that are iodine or sulfur

- A (1 rows): Return two separate numbers: the count of distinct iodine atoms that take part in a single bond, and the count of distinct sulfur atoms that take part in a single bond.
- B (1 rows, changes the answer): Return one number: the total count of distinct atoms that are iodine or sulfur and take part in a single bond.

**Reviews:** opus: {'A': 'fits', 'B': 'fits'}; sonnet: {'B': 'fits', 'A': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [stated] start from atoms -- "How many atoms"
- [implied] link atom to connected via atom_id (first atom) -- "atoms ... in single bond molecules"
- [implied] link connected to bond via bond_id -- "in single bond molecules"
- [via_evidence] filter bond_type = '-' -- "single type bond refers to bond_type = '-'"
- [via_evidence] iodine means element = 'i' -- "with iodine element refer to element = 'i'"
- [via_evidence] sulfur means element = 's' -- "with sulfur element refers to element = 's'"
- [via_evidence] count distinct atom ids -- "Should consider the distinct atoms when counting"
- [left_open] output two separate counts, one for iodine and one for sulfur -- "How many atoms with iodine and with sulfur type elements"
- [implied] all qualifying rows form one group giving one result row -- "How many"
- [implied] missing values: non-matching elements do not count -- "atoms with iodine and with sulfur"

**Open phrase:** "How many atoms with iodine and with sulfur type elements are there" -- The single 'How many' suggests one total over the union of the two elements, but the repeated 'with iodine and with sulfur' can also be read as asking for each element's count separately.

**Pattern:**
- asks with a single 'how many' but names two categories joined by 'and', so it is unclear whether the output has one column or two
- leaves the join path implicit in a loose phrase ('in single bond molecules') that actually means atoms taking part in bonds of that type
- puts the code values for categories and filter values in the evidence, not the question
- states distinct counting only in the evidence
- says nothing about output column names or layout

## batch1 b029 (toxicology) -- aggregation_level, disputed

**Original:** List all the elements of atoms that can not bond with any other atoms. | Evidence:  atoms cannot bond with other atoms means atom_id NOT in connected table;

**Decision:** Whether the 'cannot bond' test applies to each atom (list the element of any unbonded atom) or to the element as a whole (list only elements where none of the atoms are bonded).

- A (3 rows): List the elements where no atom of that element appears in the connected table. If any atom of an element is bonded, that element is left out.
- B (5 rows, changes the answer): List the distinct elements of the individual atoms whose atom_id does not appear in the connected table, even if other atoms of the same element are bonded.
- C0 (5 rows, changes the answer): Atom-level test that counts an atom as bonded if it appears in either column of the connected table (atom_id or atom_id2).

**Reviews:** opus: {'B': 'fits', 'A': 'fits', 'C0': 'fits'}; sonnet: {'C0': 'fits', 'A': 'does not fit', 'B': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [stated] start from atom records -- "elements of atoms"
- [via_evidence] link atom to connected on atom_id = connected.atom_id (first-atom side only) -- "atom_id NOT in connected table"
- [left_open] exclusion is at element level: drop an element if any atom of that element appears in connected -- "elements of atoms that can not bond with any other atoms"
- [implied] check membership against connected.atom_id only, not atom_id2 -- "atom_id NOT in connected table"
- [left_open] NOT IN null semantics (missing element makes the result undetermined) -- ""
- [stated] output column: atom.element -- "List all the elements"
- [implied] remove duplicate elements -- "List all the elements"
- [implied] no ordering or limit -- ""

**Open phrase:** "elements of atoms that can not bond with any other atoms" -- The evidence speaks about the individual atom ('atom_id NOT in connected table'), which supports a per-atom filter, while 'elements ... that can not bond' can also be read as a property of the element itself, meaning no atom of that element is ever bonded.

**Pattern:**
- uses a relative clause that could attach to either the listed attribute or the entity it belongs to
- evidence turns a domain phrase into an anti-membership test on an identifier but does not say at what level the test applies
- leaves the null behavior of the exclusion test unstated
- asks to 'list all' an attribute and leaves deduplication to convention
- names only one of two possible link columns, so the check on the other side is left out without comment

## batch1 b036 (superhero) -- aggregation_level, disputed

**Original:** Please list the full names of all the superheroes with over 15 super powers. | Evidence: 15 super powers refers to COUNT(full_name) > 15

**Decision:** The unit powers are counted over: each hero (superhero.id), or each distinct full_name value, which pools the powers of heroes who share a name, including NULL or '-'

- A (71 rows): Group the hero-power rows by full_name, so all heroes with the same full name (including missing names such as NULL or '-') count as one unit, and list each full name whose combined power count is over 15.
- B (65 rows, changes the answer): Count powers separately for each superhero, identified by id, and list the full name of every hero who has more than 15 powers.

**Reviews:** opus: {'B': 'fits', 'A': 'does not fit'}; sonnet: {'A': 'fits', 'B': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [stated] start from superhero records -- "superheroes"
- [implied] link superhero to hero_power via id = hero_id (inner join) -- "superheroes with over 15 super powers"
- [left_open] group by full_name (not by hero id) -- "the full names of all the superheroes with over 15 super powers"
- [via_evidence] count non-missing power_id per group -- "15 super powers refers to COUNT(full_name) > 15"
- [stated] keep groups with count greater than 15 (strict) -- "over 15"
- [stated] output column: full_name -- "list the full names"
- [left_open] remove duplicate result rows -- "list the full names of all the superheroes"
- [left_open] handling of missing/placeholder full names -- ""
- [implied] no ordering or limit -- "list ... all the superheroes"

**Open phrase:** "full names of all the superheroes with over 15 super powers" -- The sentence says each superhero has the powers, which points to counting per hero id. But the evidence 'COUNT(full_name)' and the output column focus on full names, so a reader could also take full_name as the grouping key and pool heroes who share a name or have a missing name.

**Pattern:**
- names the counted property per entity ('superheroes with over N X') without saying which key identifies an entity
- evidence gives the count as a pseudo-SQL aggregate over the output column, not the counted column, which blurs the grouping key
- states the threshold with a strict comparative ('over N')
- asks for a descriptive attribute that may not be unique, and says nothing about duplicate or missing values
- the table link is left to the schema rather than stated

## batch1 b038 (superhero) -- output_form, mutually recognized

**Original:** Between DC and Marvel Comics, which publisher has published more superheroes? Find the difference in the number of superheroes they have published. | Evidence: DC refers to publisher_name = 'DC Comics'; Marvel Comics refers to publisher_name = 'Marvel Comics'; calculation = SUBTRACT(SUM(publisher_name = 'Marvel Comics'), SUM(publisher_name = 'DC Comics'))

**Decision:** Output form: return only the numeric difference, or also return which publisher has more superheroes alongside the difference

- A (1 rows): Return a single value: the number of Marvel Comics superheroes minus the number of DC Comics superheroes, following the evidence's calculation.
- B (1 rows, changes the answer): Answer both parts of the question: name the publisher with more superheroes, and give the difference in their superhero counts.
- C0 (1 rows, changes the answer): Name the publisher with more superheroes and give the difference as a size that is always positive, whichever publisher is larger.

**Reviews:** opus: {'B': 'fits', 'C0': 'fits', 'A': 'fits'}; sonnet: {'A': 'fits', 'C0': 'fits', 'B': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [implied] start from superhero records -- "superheroes"
- [implied] link each superhero to its publisher via publisher_id = publisher.id, dropping unmatched -- "which publisher has published more superheroes"
- [via_evidence] identify Marvel as publisher_name = 'Marvel Comics' -- "Marvel Comics refers to publisher_name = 'Marvel Comics'"
- [via_evidence] identify DC as publisher_name = 'DC Comics' -- "DC refers to publisher_name = 'DC Comics'"
- [implied] all records form one group giving one result row -- "Find the difference in the number of superheroes they have published"
- [via_evidence] count superheroes per publisher as sum of 1/0 indicators -- "SUM(publisher_name = 'Marvel Comics'), SUM(publisher_name = 'DC Comics')"
- [via_evidence] compute Marvel count minus DC count (signed, in that order) -- "calculation = SUBTRACT(SUM(publisher_name = 'Marvel Comics'), SUM(publisher_name = 'DC Comics'))"
- [contradicted] output only the difference, no publisher-name column -- "which publisher has published more superheroes?"
- [left_open] missing values ignored in sums -- ""
- [implied] no ordering or limit -- ""

**Open phrase:** "which publisher has published more superheroes? Find the difference in the number of superheroes they have published." -- The question asks two things, which calls for a name and a number, but the evidence gives only the subtraction, and a signed Marvel-minus-DC value already shows which publisher is ahead.

**Pattern:**
- asks a two-part question (which entity is larger, and by how much) but the evidence formalizes only the second part
- fixes the order of subtraction in the evidence, so the sign of the result encodes the answer to the comparison
- maps informal entity names to exact stored category values through evidence
- leaves the join between the counted entity and its category table implied by the word 'published'
- gives no rule for missing values or ties between the two counts

## batch1 b042 (superhero) -- tie, mutually recognized

**Original:** Which hero was the fastest? | Evidence: which hero refers to superhero_name; fastest refers to MAX(attribute_value) WHERE attribute_name = 'Speed';

**Decision:** How to handle the 40 heroes tied at the maximum Speed value: return only one of them or return all of them

- A (1 rows): Return a single hero: the first row after sorting by Speed value from highest to lowest (LIMIT 1). When several heroes tie, the one returned is arbitrary.
- B (40 rows, changes the answer): Return every hero whose Speed value equals the maximum Speed value, including all tied heroes.

**Reviews:** opus: {'B': 'fits', 'A': 'fits'}; sonnet: {'A': 'fits', 'B': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [stated] start from superhero records -- "Which hero"
- [implied] link superhero to hero_attribute via hero id -- "fastest"
- [via_evidence] link hero_attribute to attribute via attribute id -- "attribute_name = 'Speed'"
- [via_evidence] filter attribute_name = 'Speed' -- "fastest refers to MAX(attribute_value) WHERE attribute_name = 'Speed'"
- [via_evidence] output superhero_name -- "which hero refers to superhero_name"
- [via_evidence] order by attribute_value descending -- "fastest refers to MAX(attribute_value)"
- [implied] keep only the first 1 row -- "Which hero was the fastest"
- [left_open] missing attribute values sorted last -- ""
- [left_open] tie handling among equally fast heroes -- "the fastest"
- [implied] drop heroes without matching attribute rows (inner joins) -- "fastest"

**Open phrase:** "Which hero was the fastest?" -- The singular 'which hero' and 'the fastest' suggest a single answer, but the evidence's MAX(attribute_value) reads naturally as 'equals the maximum', which would return every tied hero, and neither the question nor the evidence says how to handle ties.

**Pattern:**
- names the extreme with a singular superlative and states no tie rule
- uses evidence to map everyday words onto a column and an aggregate (MAX) instead of saying how rows are sorted or limited
- puts the attribute filter only in the evidence as a literal value condition
- leaves the join path through the linking table unstated, to be inferred from the schema
- says nothing about missing values

## batch1 b043 (superhero) -- tie, disputed

**Original:** What is the race of the superhero with maximum attribute value? | Evidence: maximum attribute value refers to MAX(attribute_value);

**Decision:** How to handle ties when several heroes share the maximum attribute value: return one arbitrary hero's race, or the races of all tied heroes

- A (1 rows): Find the single top row by attribute_value (one arbitrary hero among any ties) and return that hero's race.
- B (25 rows, changes the answer): Find every hero with an attribute value equal to the overall maximum and return the distinct races of all of them.

**Reviews:** opus: {'B': 'fits', 'A': 'fits'}; sonnet: {'B': 'fits', 'A': 'does not fit'}

**How the real question carries each requirement of the explicit specification:**

- [stated] start from superhero records -- "the superhero"
- [implied] link superhero to hero_attribute via hero id (inner join) -- "superhero with maximum attribute value"
- [implied] link superhero to race via race_id (inner join) -- "race of the superhero"
- [via_evidence] rank by attribute_value, highest first -- "maximum attribute value refers to MAX(attribute_value)"
- [implied] maximum taken over all attribute rows, regardless of attribute type -- "maximum attribute value"
- [stated] output column: race name -- "What is the race"
- [implied] keep only the single top row (limit 1) -- "the superhero"
- [left_open] missing attribute values sorted last -- ""
- [left_open] tie handling: pick one arbitrary top hero -- ""
- [left_open] duplicates: no deduplication of race values -- ""

**Open phrase:** "the superhero with maximum attribute value" -- The singular 'the superhero' suggests there is only one answer, but MAX(attribute_value) is a value that many heroes can share, so a careful reader could return one row or every race among the tied heroes.

**Pattern:**
- names the extreme with a singular definite noun phrase ('the X with maximum Y') and gives no tie rule
- uses evidence to map the superlative to an aggregate function, not to an ordering-plus-limit
- leaves the join path through the linking table and the lookup table to be inferred from the entity and attribute names
- doesn't say which attribute type is ranked, which suggests all attribute rows are pooled
- says nothing about missing values or duplicate output values

## batch1 b056 (thrombosis_prediction) -- tie, mutually recognized

**Original:** For the patient who has the highest Ig A within the normal range, what is his or her diagnosis? | Evidence: highest Ig A within the normal range refers to MAX(IGA BETWEEN 80 AND 500);

**Decision:** How to handle several lab records tied at the maximum in-range IgA value (IGA = 500): return one row or every tied patient's diagnosis.

- A (1 rows): Return a single diagnosis, taken from one lab record with the highest IgA between 80 and 500. When several records tie, whichever one sorts first wins.
- B (4 rows, changes the answer): Return the diagnoses of all patients whose lab record matches the highest IgA between 80 and 500, so every tied patient is included.
- C0 (4 rows, changes the answer): Return one row per tied lab record, keeping duplicate diagnoses, so every tied record is listed separately.

**Reviews:** opus: {'B': 'fits', 'A': 'fits', 'C0': 'fits'}; sonnet: {'C0': 'does not fit', 'B': 'fits', 'A': 'fits'}

**How the real question carries each requirement of the explicit specification:**

- [implied] start from patients linked to their lab records by patient ID -- "the patient who has the highest Ig A"
- [implied] drop patients with no matching lab record (inner join) -- "the patient who has the highest Ig A"
- [via_evidence] filter IgA between 80 and 500 inclusive -- "within the normal range refers to MAX(IGA BETWEEN 80 AND 500)"
- [stated] pick the maximum IgA among the kept records -- "highest Ig A"
- [stated] output column: the diagnosis -- "what is his or her diagnosis"
- [implied] order by IgA descending, missing values last -- "highest"
- [implied] return only 1 row -- "For the patient"
- [left_open] tie handling: keep only whichever top record sorts first -- ""
- [left_open] duplicate diagnoses / several lab rows for one patient -- ""

**Open phrase:** "For the patient who has the highest Ig A" -- The singular 'the patient' suggests there is exactly one answer, but 'highest' names a value that several lab records or patients could share, and neither the question nor the evidence says what to do when they tie.

**Pattern:**
- names the extreme with a singular superlative ('the patient who has the highest') and gives no tie rule
- puts the range filter in evidence written as pseudo-code (MAX(... BETWEEN ...)), which mixes the filter and the aggregate together
- never mentions the link between patients and lab records; the possessive wording implies it
- asks for one attribute of the chosen entity using conversational pronouns ('his or her')
- says nothing about multiple lab records per patient or duplicate output rows

