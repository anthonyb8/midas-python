import unittest

if __name__ == "__main__":
    # This will discover and run all tests in the directory and subdirectories.
    loader = unittest.TestLoader()
    start_dir = '.'  # Assuming main_test.py is in the root directory of your tests
    print(start_dir)
    suite = loader.discover(start_dir, pattern='test_*.py') 
    print(suite)

    runner = unittest.TextTestRunner()
    runner.run(suite)
