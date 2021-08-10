import aspectlib
import random

def fizzbuzz(num: int) -> str:
    fizz = num % 3 == 0
    buzz = num % 5 == 0

    if fizz and buzz:
        return "FizzBuzz"
    elif fizz:
        return "Fizz"
    elif buzz:
        return "Buzz"
    else:
        return str(num)

FIZZBUZZ_SAMPLING_RATE = 0.05 # Should log the function 10% of the times

fizzbuzz_aspect_count = 0 # Holds how many the aspect is hit

@aspectlib.Aspect
def fizzbuzz_aspect(*args):
    global fizzbuzz_aspect_count

    # If the random value is greater than the FIZZBUZZ_SAMPLING_RATE
    # the aspect should proceed with the instrumented function and then stop.
    if random.random() > FIZZBUZZ_SAMPLING_RATE:
        yield
        return
    fizzbuzz_aspect_count += 1
    yield
aspectlib.weave(fizzbuzz, fizzbuzz_aspect)

N = 10000
for i in range(1, N):
    print(fizzbuzz(i))
print(f"FizzBuzz aspect hit count: {fizzbuzz_aspect_count * 100 / N}%")