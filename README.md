# Responsys REST API Python Wrapper
My take on a Python wrapper for the Responsys REST API.

## TODOs:
1. -NEXT- Series of if statements or ternary conditional operators for query parameters.
2. For fetch_all_campaigns and fetch_all_programs, consider parsing the next query parameter values within the next href instead of using the whole href as a replacement for resource_path.
3. Check if STR100 and other types work for supplemental tables and profile extension tables.
4. Implement optional SQLite/PostgreSQL storage separately.
5. -NEXT- Check viability of using generators instead of the complete fetch functions.
6. Consider adding asynchronous functionality to the \_try_requests_function.
7. Decide if config.py is for rsys_api.py or for demo.py.
