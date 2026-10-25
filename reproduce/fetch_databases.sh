#!/bin/sh
# The 155 source databases the generator runs on (Spider and BIRD databases, CC BY-SA 4.0; LiveSQLBench databases, CC BY 4.0),
# as snapshotted for the paper (557 MB; one file exceeds GitHub's 100 MB file limit, so they are a release asset, not repository
# files). Needed only to rerun query generation and the 152-database coverage run (Sections 2.2 and 4.2); the 12 evaluation
# databases are already in benchmark/databases/. Replaces the link out/gamma_pool/snapshot -> benchmark/databases with the full set.
set -e
U=https://github.com/Xyc-arch/specbridge-artifact/releases/download/v1.0/source-databases.tar.gz
D=out/gamma_pool/snapshot; T=$(mktemp -d)
curl -fL $U -o $T/db.tar.gz
rm -rf $D; mkdir -p $D; tar xzf $T/db.tar.gz -C $D; rm -rf $T
cd $D && (command -v sha256sum >/dev/null && sha256sum -c ../../../reproduce/source_databases.sha256 || shasum -a 256 -c ../../../reproduce/source_databases.sha256)
