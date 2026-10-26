# Ambiguity methods on 100 request sets (`specbridge.comm.transfer.reqmethod`)

Answer sets after dropping identical results (every arm). Computable miss: a reading the plain open answer missed that the solver computes from its specific request in one call. Paired bootstrap over sets for ours vs each arm.

## sonnet (111 sets; 44 computable misses)

| arm | open: both readings | open: names the choice | computable misses recovered | specific: main right | specific: false alarm | answers per wording | calls / chars in per wording |
|---|---|---|---|---|---|---|---|
| plain | 64 / 111 | 69 / 111 | 0 of 44 | 109 / 111 | 0 | 1.4 | 1 / saved |
| samplek | 72 / 111 | 70 / 111 | 11 of 44 | 108 / 111 | 0 | 1.6 | 3.0 / 46320 |
| dtp | 10 / 111 | 95 / 111 | 4 of 44 | 72 / 111 | 3 | 4.2 | 8.0 / 122050 |
| ours | 78 / 111 | 75 / 111 | 17 of 44 | 109 / 111 | 0 | 1.5 | 2.6 / 39324 |
| ours+lib | 79 / 111 | 75 / 111 | 17 of 44 | 109 / 111 | 32 | 2.3 | 2.6 / 39324 |
ours - dtp (paired): both readings +0.61 [0.51, 0.70]; names the choice -0.18 [-0.27, -0.09]; computable misses recovered +0.30 [0.16, 0.45].
ours - samplek (paired): both readings +0.05 [0.00, 0.12]; names the choice +0.05 [-0.05, 0.14]; computable misses recovered +0.14 [0.00, 0.27].
ours - plain (paired): both readings +0.13 [0.05, 0.20]; names the choice +0.05 [-0.05, 0.15]; computable misses recovered +0.39 [0.25, 0.55].
ours+lib - dtp (paired): both readings +0.62 [0.53, 0.71]; names the choice -0.18 [-0.27, -0.09]; computable misses recovered +0.30 [0.16, 0.45].
ours+lib - samplek (paired): both readings +0.06 [0.00, 0.13]; names the choice +0.05 [-0.05, 0.14]; computable misses recovered +0.14 [-0.02, 0.30].
ours+lib - plain (paired): both readings +0.14 [0.07, 0.21]; names the choice +0.05 [-0.04, 0.15]; computable misses recovered +0.39 [0.25, 0.52].

## gpt-6-sol (111 sets; 74 computable misses)

| arm | open: both readings | open: names the choice | computable misses recovered | specific: main right | specific: false alarm | answers per wording | calls / chars in per wording |
|---|---|---|---|---|---|---|---|
| plain | 47 / 111 | 54 / 111 | 0 of 74 | 92 / 111 | 0 | 1.2 | 1 / saved |
| samplek | 60 / 111 | 61 / 111 | 17 of 74 | 92 / 111 | 0 | 1.4 | 3.0 / 46320 |
| dtp | 35 / 111 | 81 / 111 | 20 of 74 | 84 / 111 | 0 | 2.5 | 5.3 / 80109 |
| ours | 62 / 111 | 61 / 111 | 32 of 74 | 106 / 111 | 0 | 1.5 | 2.5 / 37419 |
| ours+lib | 66 / 111 | 61 / 111 | 36 of 74 | 106 / 111 | 34 | 2.2 | 2.5 / 37419 |
ours - dtp (paired): both readings +0.24 [0.13, 0.35]; names the choice -0.18 [-0.28, -0.08]; computable misses recovered +0.16 [0.01, 0.28].
ours - samplek (paired): both readings +0.02 [-0.06, 0.10]; names the choice +0.00 [-0.08, 0.09]; computable misses recovered +0.20 [0.09, 0.32].
ours - plain (paired): both readings +0.14 [0.05, 0.22]; names the choice +0.06 [-0.04, 0.17]; computable misses recovered +0.43 [0.32, 0.54].
ours+lib - dtp (paired): both readings +0.28 [0.18, 0.39]; names the choice -0.18 [-0.28, -0.07]; computable misses recovered +0.22 [0.08, 0.35].
ours+lib - samplek (paired): both readings +0.05 [-0.03, 0.14]; names the choice +0.00 [-0.09, 0.08]; computable misses recovered +0.26 [0.14, 0.38].
ours+lib - plain (paired): both readings +0.17 [0.09, 0.25]; names the choice +0.06 [-0.04, 0.16]; computable misses recovered +0.49 [0.38, 0.61].

