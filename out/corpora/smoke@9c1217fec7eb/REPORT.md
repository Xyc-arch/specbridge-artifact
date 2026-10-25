# Corpus `smoke@9c1217fec7eb`

Request: `{"name": "smoke", "count": 6, "seed": 5, "databases": {"college_2": 1}, "target": {"preset": "medium"}, "standard": "benchmark", "max_move": {"arith": 1, "steps": 1}}`

Grammar compose-v3.1 (frozen), rubric v1.1, standard **benchmark**. Complexity integrity: not assessed.

**6 of 6 tasks delivered** in 17 s with 18 model calls (2.8 s and 3.0 calls per delivered task).

## By database

| database | planned | delivered | generated | reviewed now | review reused | failed the standard | packaging refused | seconds |
|---|---|---|---|---|---|---|---|---|
| college_2 | 6 | 6 | 9 | 9 | 0 | 0 | 0 | 16.8 |

## Requested vs delivered by depth cell (all databases)

| A,S | requested | delivered |
|---|---|---|
| 0,2 | 0 | 1 |
| 1,2 | 1 | 0 |
| 1,3 | 1 | 3 |
| 1,4 | 1 | 2 |
| 2,2 | 1 | 0 |
| 2,3 | 1 | 0 |
| 2,4 | 1 | 0 |

Operations used: {'baseline': 4, 'aggregate only': 1, 'share': 1}

Diversity: 6 distinct computations, 2 base quantities, 5 tables, 6 constructions.

## Shortfalls

None.

## A random sample of delivered tasks

- **college_2** A1 S3 `agg:student.dept_name > baseline:all`
  - Step 1. Start from each `advisor` record; combine it with each `student` record for which Student ID (`student.ID`) equals Student ID (`advisor.s_ID`) (compared as text, character by character), one combined record per match (a record without a match is dropped); group the kept records by Department names (`student.dept_name`); each group gives one result row; for each result row, return (1) Department names (`student.dept_name`); (2) the number of records in the group. / Step 2. Start from the ro
- **college_2** A1 S4 `agg:instructor (by ID) > baseline:all > agg:all`
  - Step 1. Start from each `teaches` record; group the kept records by Instructor ID (`teaches.ID`); each group gives one result row; for each result row, return (1) Instructor ID (`teaches.ID`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step 3. Start from the rows of 
- **college_2** A0 S2 `agg:department (by dept_name) > agg:all`
  - Step 1. Start from each `student` record; group the kept records by Department names (`student.dept_name`); each group gives one result row; for each result row, return (1) Department names (`student.dept_name`); (2) the average of total credits earned (`student.tot_cred`) in the group (missing values ignored; missing when there are none); (3) the number of records in the group. / Step 2 (the answer). Start from the rows of step 1; all kept records form one group, which gives one result row; for e
- **college_2** A1 S4 `agg:department (by dept_name) > baseline:all > agg:all`
  - Step 1. Start from each `course` record; group the kept records by Department names (`course.dept_name`); each group gives one result row; for each result row, return (1) Department names (`course.dept_name`); (2) the average of course credit hours (`course.credits`) in the group (missing values ignored; missing when there are none). / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of ste
- **college_2** A1 S3 `agg:course within course.dept_name > baseline:all`
  - Step 1. Start from each `prereq` record; combine it with each `course` record for which Unique identifier for each course (`course.course_id`) equals Course identifiers (`prereq.course_id`) (compared as text, character by character), one combined record per match (a record without a match is dropped); group the kept records by Course identifiers (`prereq.course_id`) and Department names (`course.dept_name`); each group gives one result row; for each result row, return (1) Course identifiers (`pr
- **college_2** A1 S3 `agg:course.dept_name > share:all`
  - Step 1. Start from each `prereq` record; combine it with each `course` record for which Unique identifier for each course (`course.course_id`) equals Course prerequisites (`prereq.prereq_id`) (compared as text, character by character), one combined record per match (a record without a match is dropped); group the kept records by Department names (`course.dept_name`); each group gives one result row; for each result row, return (1) Department names (`course.dept_name`); (2) the number of records 
