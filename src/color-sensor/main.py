import RPi.GPIO as GPIO
import time

S2_PIN = 19
S3_PIN = 13
OUTPUT_PIN = 26
CYCLES_TO_WAIT = 3


def hue_saturation_from_rgb(r, g, b):
    c_max = max(r, g, b)
    c_min = min(r, g, b)
    delta = c_max - c_min
    hue = 0
    saturation = 0

    if delta == 0:
        hue = 0
    elif c_max == r:
        hue = 60 * ((g - b) / delta % 6)
    elif c_max == g:
        hue = 60 * ((b - r) / delta + 2)
    elif c_max == b:
        hue = 60 * ((r - g) / delta + 4)
    if c_max != 0:
        saturation = delta / c_max

    return hue, saturation


# needs to be calibrated when changing lighting
def normalize_frequency(freq):
    return min(1, max(0, (freq - 250) / 4000))


def get_raw_frequency(S2_VALUE, S3_VALUE):
    GPIO.output(S2_PIN, S2_VALUE)
    GPIO.output(S3_PIN, S3_VALUE)
    time.sleep(0.001)
    GPIO.wait_for_edge(OUTPUT_PIN, GPIO.FALLING)
    start = time.time()

    for impulse_count in range(CYCLES_TO_WAIT):
        GPIO.wait_for_edge(OUTPUT_PIN, GPIO.FALLING)

    duration = time.time() - start  # seconds to run for loop
    frequency = CYCLES_TO_WAIT / duration  # in Hz
    return frequency


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OUTPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(S2_PIN, GPIO.OUT)
    GPIO.setup(S3_PIN, GPIO.OUT)
    print("\n")


if __name__ == "__main__":
    setup()
    try:
        curr_color = prev_color = " "
        change_time = 0
        while True:
            curr_time = time.time()

            red_frequency = get_raw_frequency(GPIO.LOW, GPIO.LOW)
            blue_frequency = get_raw_frequency(GPIO.LOW, GPIO.HIGH)
            green_frequency = get_raw_frequency(GPIO.HIGH, GPIO.HIGH)
            norm_red = normalize_frequency(red_frequency)
            norm_blue = normalize_frequency(blue_frequency)
            norm_green = normalize_frequency(green_frequency)

            hue, saturation = hue_saturation_from_rgb(norm_red, norm_green, norm_blue)

            if 320 < hue < 360 and prev_color != "blue" and temp_color != "red":
                temp_color = "red"
                change_time = curr_time
            elif 120 < hue < 180 and prev_color != "yellow" and temp_color != "green":
                temp_color = "green"
                change_time = curr_time
            elif 200 < hue < 240 and prev_color != "red" and temp_color != "blue":
                temp_color = "blue"
                change_time = curr_time
            elif 10 < hue < 50 and prev_color != "green" and temp_color != "yellow":
                temp_color = "yellow"
                change_time = curr_time

            if curr_time - change_time >= 0.06:
                curr_color = temp_color

            if curr_color != prev_color:
                print(curr_color)

            prev_color = curr_color
    finally:
        GPIO.cleanup()
