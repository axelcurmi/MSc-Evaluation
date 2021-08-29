$out = 'out/Docker_500KB_Full';

$experiments = @("500KB-1", "500KB-10", "500KB-100", "500KB-1000")

foreach ($i in $experiments) {
    # [-] RV
    # [-] SEcube
    New-Item "${out}/F_F/${i}" -ItemType Directory -ErrorAction SilentlyContinue
    mprof run --out "${out}/F_F/${i}/F_F_0.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --no-calc-stats --out ${out}
    mprof run --out "${out}/F_F/${i}/F_F_1.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --no-calc-stats --out ${out}
    mprof run --out "${out}/F_F/${i}/F_F_2.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --out ${out}

    # [+] RV
    # [-] SEcube
    New-Item "${out}/T_F/${i}" -ItemType Directory -ErrorAction SilentlyContinue
    mprof run --out "${out}/T_F/${i}/T_F_0.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-instrumentation --no-calc-stats --out ${out}
    mprof run --out "${out}/T_F/${i}/T_F_1.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-instrumentation --no-calc-stats --out ${out}
    mprof run --out "${out}/T_F/${i}/T_F_2.dat" src/experiment_runner.py `
    config.json "instructions/memory/docker/docker_${i}.json" --with-instrumentation --out ${out}
}
