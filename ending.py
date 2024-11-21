async def main():
    """Main asynchronous function."""
    await asyncio.gather(
        update_sensors(),
        cooling1(),
        heating2(),
        run_gui(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated.")
    finally:
        sensor1.exit()
        sensor2.exit()
        GPIO.cleanup()
