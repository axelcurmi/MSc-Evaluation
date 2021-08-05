$out = 'out/Docker_512KB_Full';

$experiments = @("512KB-1", "512KB-10", "512KB-100", "512KB-1000")

foreach ($i in $experiments) {
    # [-] RV
    # [+] SEcube
    New-Item "${out}/F_T/${i}" -ItemType Directory -ErrorAction SilentlyContinue
    mprof run --out "${out}/F_T/${i}/F_T_0.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-secube --no-calc-stats --out ${out}
    mprof run --out "${out}/F_T/${i}/F_T_0.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-secube --no-calc-stats --out ${out}
    mprof run --out "${out}/F_T/${i}/F_T_0.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-secube --out ${out}

    # [+] RV
    # [+] SEcube
    New-Item "${out}/T_T/${i}" -ItemType Directory -ErrorAction SilentlyContinue
    mprof run --out "${out}/T_T/${i}/T_T_0.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-instrumentation --with-secube --no-calc-stats --out ${out}
    mprof run --out "${out}/T_T/${i}/T_T_0.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-instrumentation --with-secube --no-calc-stats --out ${out}
    mprof run --out "${out}/T_T/${i}/T_T_0.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-instrumentation --with-secube --out ${out}
}
