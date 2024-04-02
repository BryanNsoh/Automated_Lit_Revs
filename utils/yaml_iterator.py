"""
   Comprehensive guide on how to use the YAML iterator with the provided YAML structure.

   Initializing the IrrigationData class:
   Create an instance of the IrrigationData class by passing the path to your YAML file as a parameter.
   Example:
   >>> data = IrrigationData("path/to/your/yaml/file.yaml")

   Loading the YAML data:
   Before you can iterate through the data or perform any operations, you need to load the YAML data from the file.
   Use the load_data method to asynchronously load the data.
   Example:
   >>> await data.load_data()

   Iterating through the entire YAML structure:
   Use the iterate_data method to iterate through the entire YAML structure asynchronously.
   The method yields the subsection, point title, query type, query ID, response ID, and response for each response in the YAML structure.
   Example:
   >>> async for subsection, point_title, query_type, query_id, response_id, response in data.iterate_data():
   ...     print(f"Subsection: {subsection['subsection_title']}")
   ...     print(f"Point: {point_title}")
   ...     print(f"Query Type: {query_type}")
   ...     print(f"Query ID: {query_id}")
   ...     print(f"Response ID: {response_id}")
   ...     print(f"Response: {response}")

   Updating specific fields of a response:
   Use the update_response method to update specific fields of a response.
   Pass the query ID, response ID, field name, and new value as parameters to the method.
   The method will search for the corresponding response in the YAML structure and update the specified field with the provided value.
   Example:
   >>> await data.update_response(query_id, response_id, "DOI", "10.1234/example")
   >>> await data.update_response(query_id, response_id, "pdf_link", "https://example.com/paper.pdf")

   Saving the updated data:
   After making any updates to the responses, you need to save the modified data back to the YAML file.
   The update_response method automatically saves the data after each update.
   If you want to manually save the data, you can use the save_data method.
   Example:
   >>> await data.save_data()

   Combining iteration and updating:
   You can combine the iteration and updating operations to process and modify the responses in a single loop.
   Example:
   >>> async for subsection, point_title, query_type, query_id, response_id, response in data.iterate_data():
   ...     # Perform operations on the response
   ...     # ...
   ...
   ...     # Update specific fields of the response
   ...     await data.update_response(query_id, response_id, "DOI", "10.1234/example")
   ...     await data.update_response(query_id, response_id, "pdf_link", "https://example.com/paper.pdf")

   Accessing specific subsections, points, queries, or responses:
   If you need to access specific subsections, points, queries, or responses, you can use conditional statements within the iteration loop.
   Example (accessing a specific subsection):
   >>> async for subsection, point_title, query_type, query_id, response_id, response in data.iterate_data():
   ...     if subsection["subsection_title"] == "Desired Subsection":
   ...         # Perform operations on the desired subsection
   ...         # ...

   Handling exceptions:
   If any exceptions occur during the iteration or updating process, you can wrap the relevant code in a try-except block to handle the exceptions gracefully.
   Example:
   >>> try:
   ...     async for subsection, point_title, query_type, query_id, response_id, response in data.iterate_data():
   ...         # Perform operations
   ...         # ...
   ... except Exception as e:
   ...     print(f"An error occurred: {str(e)}")

   Closing the loop:
   After you have finished iterating through the data and performing any necessary operations, the loop will automatically end.
   You can perform any post-processing or cleanup tasks after the loop.

   Remember to use the async/await syntax appropriately when working with asynchronous methods and loops.
   """

import asyncio
import aiofiles
import shutil
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


from ruamel.yaml import YAML


class IrrigationData:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.yaml = YAML()
        self.data = None

    async def load_data(self):
        try:
            async with aiofiles.open(self.yaml_file, "r") as file:
                content = await file.read()
                self.data = self.yaml.load(content)
        except Exception as e:
            logger.exception("An error occurred while loading YAML data.")
            raise

    async def save_data(self):
        try:
            # Create a temporary file to write the updated data
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                self.yaml.dump(self.data, temp_file)
                temp_file_path = temp_file.name

            # Replace the original file with the temporary file
            shutil.move(temp_file_path, self.yaml_file)
            logger.info("Saved updated YAML data.")
        except Exception as e:
            logger.exception("An error occurred while saving YAML data.")
            # Attempt to restore from the backup file
            await self.restore_from_backup()
            raise

    async def save_data_with_backup(self):
        try:
            # Create a backup of the original YAML file
            backup_file = f"{self.yaml_file}.bak"
            shutil.copy2(self.yaml_file, backup_file)
            logger.info(f"Created backup of YAML file: {backup_file}")

            # Save the updated data
            await self.save_data()
        except Exception as e:
            logger.exception("An error occurred while saving YAML data with backup.")
            raise

    async def restore_from_backup(self):
        backup_file = f"{self.yaml_file}.bak"
        if os.path.exists(backup_file):
            shutil.move(backup_file, self.yaml_file)
            logger.info(f"Restored YAML file from backup: {backup_file}")
        else:
            logger.warning("No backup file found. Unable to restore.")

    async def iterate_data(self):
        for subsection in self.data["subsections"]:
            for point in subsection["points"]:
                point_title = next(iter(point))
                point_data = point[point_title]
                query_types = [
                    key for key in point_data.keys() if key.endswith("_queries")
                ]
                for query_type in query_types:
                    queries = point_data.get(query_type, [])
                    for query_mother in queries:
                        query_id = query_mother["query_id"]
                        query = query_mother["query"]
                        for response in query_mother.get("responses", []):
                            response_id = response["response_id"]
                            yield subsection, point_title, query_type, query_id, response_id, response, query

    async def update_response(
        self, subsection_index, point_title, query_id, response_id, field, value
    ):
        subsection = self.data["subsections"][subsection_index]
        for point in subsection["points"]:
            if point_title in point:
                point_data = point[point_title]
                query_types = [
                    key for key in point_data.keys() if key.endswith("_queries")
                ]
                for query_type in query_types:
                    queries = point_data.get(query_type, [])
                    for query in queries:
                        if query["query_id"] == query_id:
                            for response in query.get("responses", []):
                                if response["response_id"] == response_id:
                                    response[field] = value
                                    await self.save_data()
                                    return


# async def main():
#     data = IrrigationData(
#         r"C:\Users\bnsoh2\OneDrive - University of Nebraska-Lincoln\Documents\Coding Projects\Automated_Lit_Revs\documents\section3\outline_queries.yaml"
#     )
#     await data.load_data()

#     async for (
#         subsection,
#         point_title,
#         query_type,
#         query_id,
#         response_id,
#         response,
#         query,
#     ) in data.iterate_data():
#         print(f"Subsection: {subsection['subsection_title']}")
#         print(f"Point: {point_title}")
#         print(f"Query Type: {query_type}")
#         print(f"Query ID: {query_id}")
#         print(f"Response ID: {response_id}")
#         print(f"Response: {response}")
#         print(f"Query: {query}")

#         # Update specific fields of the response
#         # await data.update_response(query_id, response_id, "DOI", "10.1234/example")
#         # await data.update_response(
#         #     query_id, response_id, "pdf_link", "https://example.com/paper.pdf"
#         # )


# asyncio.run(main())
