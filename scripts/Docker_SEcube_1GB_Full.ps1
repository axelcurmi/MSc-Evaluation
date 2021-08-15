$out = 'out/Docker_1GB_Full';

$experiments = @("1GB-1", "1GB-10", "1GB-100", "1GB-1000")

foreach ($i in $experiments) {
    # [-] RV
    # [+] SEcube
    New-Item "${out}/F_T/${i}" -ItemType Directory -ErrorAction SilentlyContinue
    mprof run --out "${out}/F_T/${i}/F_T_0.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-secube --no-calc-stats --out ${out}
    mprof run --out "${out}/F_T/${i}/F_T_1.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-secube --no-calc-stats --out ${out}
    mprof run --out "${out}/F_T/${i}/F_T_2.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-secube --out ${out}

    # [+] RV
    # [+] SEcube
    New-Item "${out}/T_T/${i}" -ItemType Directory -ErrorAction SilentlyContinue
    mprof run --out "${out}/T_T/${i}/T_T_0.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-instrumentation --with-secube --no-calc-stats --out ${out}
    mprof run --out "${out}/T_T/${i}/T_T_1.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-instrumentation --with-secube --no-calc-stats --out ${out}
    mprof run --out "${out}/T_T/${i}/T_T_2.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-instrumentation --with-secube --out ${out}
}
