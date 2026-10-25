# Communication library v1: 21 records ({'disputed': 10, 'mutually recognized': 11})

| source | task | db | choice | structure | semantics | decision | readings (rows; changes answer) | status |
|---|---|---|---|---|---|---|---|---|
| bird_pairs | b008 | superhero | tie | extreme_selection,aggregation_over_join | other | How to handle ties at the minimum Intelligence value: return one hero or every h | A 1; B 3 * | disputed |
| bird_pairs | b015 | superhero | tie | extreme_selection,repeated_entity_records | entity_vs_event | How to handle ties for the minimum attribute_value: return every hero that has t | A 10; B 1 *; C0 7 * | mutually recognized |
| bird_pairs | b029 | thrombosis_prediction | which_column_source | filter_only | shared_column_names,entity_vs_event | Which table's Diagnosis column should hold 'APS': the Patient record's diagnosis | A 1; B 1 *; C0 1 | mutually recognized |
| bird_pairs | b031 | thrombosis_prediction | counting_unit | ratio,aggregation_over_join,repeated_entity_records | entity_vs_event | What to count: lab test records or distinct female patients (a patient with seve | A 1; B 1 *; C0 1 * | disputed |
| bird_pairs | b032 | california_schools | missing_values | filter_only | other | Whether schools that match the filters but have no phone on record (NULL Phone)  | A 751; B 694 * | disputed |
| bird_pairs | b034 | california_schools | aggregation_level | aggregation_over_join,extreme_selection,repeated_entity_records,grouping | entity_vs_event | Whether to rank districts by one school's AvgScrRead value or by the average of  | A 1; B 1 *; C0 1 * | mutually recognized |
| bird_pairs | b041 | california_schools | other | extreme_selection,other | shared_column_names,other | Whether candidate records are limited to satscores rows that match a school in t | A 1; B 1 *; C0 1 * | mutually recognized |
| batch1 | b005 | california_schools | output_form | filter_only | other | The order of the output columns: website first and school name second, or school | A 2; B 2 * | mutually recognized |
| batch1 | b008 | california_schools | output_form | extreme_selection,grouping,repeated_entity_records | other | Which columns the answer returns: whether the county name is included next to ea | A 858; B 858 *; C0 867 *; C1 867 * | mutually recognized |
| batch1 | b011 | california_schools | which_column_source | extreme_selection | shared_column_names,other | Where the school name comes from when the top row is Los Angeles Unified's distr | A 1; B 1 *; C0 1 *; C1 1 | disputed |
| batch1 | b012 | financial | time_scope | extreme_selection | other | Whether a transaction on the account-opening date counts as 'after opened the ac | A 1; B 1 * | disputed |
| batch1 | b017 | financial | counting_unit | aggregation_over_join,repeated_entity_records | entity_vs_event | Counting unit for the average: whether each qualifying district's 1995 crime cou | A 1; B 1 *; C0 1 * | disputed |
| batch1 | b024 | toxicology | output_form | extreme_selection,grouping | coded_values | Whether the output should be only the bond type, or the bond type together with  | A 1; B 1 * | disputed |
| batch1 | b025 | toxicology | output_form | ratio,aggregation_over_join | other | Order of the arithmetic in the percentage: the gold multiplies the carbon count  | A 1; B 1 * | mutually recognized |
| batch1 | b028 | toxicology | output_form | aggregation_over_join,filter_only | coded_values | Whether to report the iodine and sulfur atom counts separately (one count per el | A 1; B 1 * | mutually recognized |
| batch1 | b029 | toxicology | aggregation_level | filter_only,repeated_entity_records | other | Whether the 'cannot bond' test applies to each atom (list the element of any unb | A 3; B 5 *; C0 5 * | disputed |
| batch1 | b036 | superhero | aggregation_level | aggregation_over_join,grouping,repeated_entity_records | other | The unit powers are counted over: each hero (superhero.id), or each distinct ful | A 71; B 65 * | disputed |
| batch1 | b038 | superhero | output_form | aggregation_over_join,extreme_selection | other | Output form: return only the numeric difference, or also return which publisher  | A 1; B 1 *; C0 1 * | mutually recognized |
| batch1 | b042 | superhero | tie | extreme_selection,aggregation_over_join | other | How to handle the 40 heroes tied at the maximum Speed value: return only one of  | A 1; B 40 * | mutually recognized |
| batch1 | b043 | superhero | tie | extreme_selection,aggregation_over_join | other | How to handle ties when several heroes share the maximum attribute value: return | A 1; B 25 * | disputed |
| batch1 | b056 | thrombosis_prediction | tie | extreme_selection,aggregation_over_join | other | How to handle several lab records tied at the maximum in-range IgA value (IGA =  | A 1; B 4 *; C0 4 * | mutually recognized |

By choice tag: {'tie': 5, 'which_column_source': 2, 'counting_unit': 2, 'missing_values': 1, 'aggregation_level': 3, 'other': 1, 'output_form': 6, 'time_scope': 1}
By structure: {'extreme_selection': 12, 'aggregation_over_join': 11, 'repeated_entity_records': 7, 'filter_only': 5, 'ratio': 2, 'grouping': 4, 'other': 1}
By semantics: {'other': 14, 'entity_vs_event': 5, 'shared_column_names': 3, 'coded_values': 2}
Records with more than two readings: 11

## Kept out of the library

- out/bird_pairs: {'one-sided': 4, 'agent mistake (no reading)': 2}; inspected causes not considered a reading: {'unwanted processing': 4, 'renderer defect': 1}
- out/comm_library/batch1: {'one-sided': 6, 'agent mistake (no reading)': 4}; inspected causes not considered a reading: {'unwanted processing': 4, 'run variation': 2}
