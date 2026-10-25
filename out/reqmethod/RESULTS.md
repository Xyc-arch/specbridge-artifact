# Ambiguity methods on 30 dev request sets (`specbridge.comm.transfer.reqmethod`)

Answer sets after dropping identical results (every arm). Computable miss: a reading the plain open answer missed that the solver computes from its specific request in one call. Paired bootstrap over sets for ours vs each arm.

## sonnet (24 sets; 9 computable misses)

| arm | open: both readings | open: names the choice | computable misses recovered | specific: main right | specific: false alarm | answers per wording | calls / chars in per wording |
|---|---|---|---|---|---|---|---|
| plain | 13 / 24 | 15 / 24 | 0 of 9 | 23 / 24 | 0 | 1.4 | 1 / saved |
| samplek | 17 / 24 | 17 / 24 | 4 of 9 | 23 / 24 | 0 | 1.7 | 3.0 / 56513 |
| dtp | 1 / 24 | 21 / 24 | 0 of 9 | 12 / 24 | 0 | 4.1 | 8.0 / 149273 |
| ours | 18 / 24 | 18 / 24 | 4 of 9 | 23 / 24 | 0 | 1.5 | 2.5 / 49078 |
| ours+lib | 18 / 24 | 18 / 24 | 4 of 9 | 23 / 24 | 0 | 1.9 | 2.5 / 49078 |
ours - dtp (paired): both readings +0.71 [0.50, 0.88]; names the choice -0.12 [-0.29, 0.00]; computable misses recovered +0.44 [0.11, 0.78].
ours - samplek (paired): both readings +0.04 [0.00, 0.12]; names the choice +0.04 [0.00, 0.12]; computable misses recovered +0.00 [0.00, 0.00].
ours - plain (paired): both readings +0.21 [0.04, 0.38]; names the choice +0.12 [0.00, 0.25]; computable misses recovered +0.44 [0.11, 0.78].
ours+lib - dtp (paired): both readings +0.71 [0.54, 0.88]; names the choice -0.12 [-0.25, 0.00]; computable misses recovered +0.44 [0.11, 0.78].
ours+lib - samplek (paired): both readings +0.04 [0.00, 0.12]; names the choice +0.04 [0.00, 0.12]; computable misses recovered +0.00 [0.00, 0.00].
ours+lib - plain (paired): both readings +0.21 [0.08, 0.38]; names the choice +0.12 [0.00, 0.29]; computable misses recovered +0.44 [0.11, 0.78].

## gpt-6-sol (24 sets; 11 computable misses)

| arm | open: both readings | open: names the choice | computable misses recovered | specific: main right | specific: false alarm | answers per wording | calls / chars in per wording |
|---|---|---|---|---|---|---|---|
| plain | 10 / 24 | 11 / 24 | 0 of 11 | 20 / 24 | 0 | 1.3 | 1 / saved |
| samplek | 15 / 24 | 17 / 24 | 5 of 11 | 20 / 24 | 0 | 1.4 | 3.0 / 56513 |
| dtp | 8 / 24 | 19 / 24 | 3 of 11 | 19 / 24 | 0 | 2.3 | 5.2 / 101671 |
| ours | 14 / 24 | 15 / 24 | 3 of 11 | 21 / 24 | 0 | 1.4 | 2.5 / 47585 |
| ours+lib | 15 / 24 | 15 / 24 | 4 of 11 | 21 / 24 | 0 | 1.8 | 2.5 / 47585 |
ours - dtp (paired): both readings +0.25 [0.04, 0.46]; names the choice -0.17 [-0.33, -0.04]; computable misses recovered +0.00 [-0.27, 0.27].
ours - samplek (paired): both readings -0.04 [-0.17, 0.08]; names the choice -0.08 [-0.21, 0.00]; computable misses recovered -0.18 [-0.45, 0.00].
ours - plain (paired): both readings +0.17 [0.04, 0.33]; names the choice +0.17 [0.04, 0.33]; computable misses recovered +0.27 [0.00, 0.55].
ours+lib - dtp (paired): both readings +0.29 [0.08, 0.50]; names the choice -0.17 [-0.33, -0.04]; computable misses recovered +0.09 [-0.18, 0.36].
ours+lib - samplek (paired): both readings +0.00 [-0.17, 0.17]; names the choice -0.08 [-0.21, 0.00]; computable misses recovered -0.09 [-0.36, 0.18].
ours+lib - plain (paired): both readings +0.21 [0.08, 0.38]; names the choice +0.17 [0.04, 0.33]; computable misses recovered +0.36 [0.09, 0.64].

