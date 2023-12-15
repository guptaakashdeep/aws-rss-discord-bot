# Lambda function code for sending back response to discord slash command.

import ssl
import os
from datetime import datetime
import json
import feedparser
import requests
import boto3
from copy import deepcopy


s3_client = boto3.client("s3")


def get_last_published_date(bucket, key):
    """
    This function retrieves the last published date from an S3 object.
    :param bucket: The name of the S3 bucket.
    :param key: The key of the S3 object.
    :return: The last published date as a string.
    :raises: Any exceptions raised by the function.

    # Retrieve the last published date from the S3 object.
    # If the object does not exist, return None.
    # If the object exists, return the last published date as a string.

    # Example usage:

    # last_published_date = get_last_published_date('my-bucket', 'last_published_date.txt')
    # print(last_published_date)

    # Example output:

    # None
    # 30-11-2023 20:15:02 +0000
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        last_published_date = response["Body"].read().decode("utf-8")
        return last_published_date
    except Exception as e:
        print(e)
        return None


def write_published_date(published_date, bucket, key):
    """
    This function writes the last published date to an S3 object.
    :param published_date: The last published date as a string.
    :param bucket: The name of the S3 bucket.
    :param key: The key of the S3 object.
    :return: None
    :raises: Any exceptions raised by the function.

    # Write the last published date to the S3 object.

    # Example usage:

    # write_published_date('30-11-2023 20:15:02 +0000', 'my-bucket', 'last_published_date.txt')

    # Example output:
    # Successfully updated last_published_date.txt
    """
    response = s3_client.put_object(Body=published_date, Bucket=bucket, Key=key)
    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        print(f"Successfully updated {key}")


def create_embeds(new_blogs_list):
    """
    This function creates a list of embeds from a list of blogs.
    It also manages embeds with characters > 6000
    :param new_blogs_list: The list of blogs.
    :return: The list of embeds.
    :raises: Any exceptions raised by the function.

    # Create a list of embeds from a list of blogs.

    # Example usage:

    # new_blogs_list = [
    #     {
    #         "title": "Blog 1",
    #         "link": "https://example.com/blog1",
    #         "summary": "This is the summary of blog 1.",
    #         "published": "2023-01-01T00:00:00+00:00",
    #         "tags": [
    #             {"term": "tag1"},
    #             {"term": "tag2"}
    #         ]
    #     }
    #                   ]
    """
    embeds = []
    for blog in new_blogs_list:
        tags = (
            ",".join([tag["term"] for tag in blog["tags"]]) if blog.get("tags") else ""
        )
        embed = {
            "title": blog["title"],
            "type": "rich",
            "url": blog["link"],
            "description": blog["summary"],
            "color": 0x36EEEE,
            "footer": {"text": blog["published"]},
            "fields": [{"name": "Tags", "value": tags}],
        }
        embeds.append(embed)
    # print("======== embeds length", total_embed_length(embeds))
    if len(embeds) > 1 and total_embed_length(embeds) > 6000:
        embeds_dict = {0: embeds}
        embeds_dict = manage_embed_length(embeds_dict)
        # print("before returning>>",embeds_dict.keys())
        return embeds_dict
    else:
        # print("inside else")
        embed_len = total_embed_length(embeds)
        if embed_len <= 6000:
            return embeds  # else manage the embed length based on internal limits.


def total_embed_length(embeds):
    """
    This function calculates the total length of an embed list.
    :param embeds: The list of embeds.
    :return: The total length of the embed list.
    :raises: Any exceptions raised by the function.

    # Calculate the total length of an embed list.

    # Example usage:

    # embeds = [
    #     {
    #         "title": "Embed 1",
    #         "description": "This is the description of embed 1."
    #     },
    #     {
    #         "title": "Embed 2",
    #         "description": "This is the description of embed 2."
    #     }
    # ]
    # total_length = total_embed_length(embeds)
    # print(total_length)

    # Example output:

    # 36
    """
    len_list = []
    for embed in embeds:
        len_list = len_list + [
            embed["title"],
            embed["description"],
            embed["fields"][0]["name"],
            embed["fields"][0]["value"],
            embed["footer"]["text"],
        ]
    return sum([len(x) for x in len_list])


def manage_embed_length(final_dict):
    """
    This function manages the length of an embed list.
    It splits the embed list into two parts and recursively calls itself to manage the length of the two parts.
    :param final_dict: The dictionary containing the embed list.
    :return: The dictionary containing the managed embed list.
    :raises: Any exceptions raised by the function.

    # Example usage:

    # final_dict = {0: [
    #     {
    #         "title": "Embed 1",
    #         "description": "This is the description of embed 1."
    #     },
    #     {
    #         "title": "Embed 2",
    #         "description": "This is the description of embed 2."
    #     }
    # ]}
    # managed_dict = manage_embed_length(final_dict)
    # print(managed_dict)

    # Example output:

    # {0: [
    #     {
    #         "title": "Embed 1",
    #         "description": "This is the description of embed 1."
    #     }
    # ], 1: [
    """
    final_dict_copy = deepcopy(final_dict)
    # print("inside managed_embed_length")
    for embed_id, embeds_list in final_dict.items():
        embed_length = total_embed_length(embeds_list)
        if embed_length > 6000:
            # print("inside >>>")
            embed_list_len = len(embeds_list)
            final_dict_copy[embed_id] = embeds_list[0 : embed_list_len // 2]
            final_dict_copy[embed_id + 1] = embeds_list[
                embed_list_len // 2 : embed_list_len
            ]
            manage_embed_length(final_dict_copy)
    return final_dict_copy


def send_response(url, headers, embeds):
    """
    This function sends a response to a slash command.
    :param url: The URL of the slash command.
    :param headers: The headers of the slash command.
    :param embeds: The payload of the slash command.
    :return: The response from the slash command.
    :raises: Any exceptions raised by the function.
    """
    response_list = []
    if isinstance(embeds, list):
        payload = {"embeds": embeds}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            print(f"Error: {response.text}")
            response_list.append(False)
        else:
            response_list.append(True)
    else: #embeds is dict instance
        for embeds_list in embeds.values():
            payload = {"embeds": embeds_list}
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code != 200:
                print(f"Error: {response.text}")
                response_list.append(False)
            else:
                response_list.append(True)
    return response_list
        


def lambda_handler(event, context):
    """
    This function is triggered when a slash command is executed.
    It will send a message back to the user.
    :param event: The event object containing the slash command data.
    :param context: The context object.
    :return: A JSON object containing the response data.
    :raises: Any exceptions raised by the function.
    :example:
    {
        "application_id": "XXXXXXXXXX",
        "token": "abcdefghijklmnopqrstuvwxyz",
        "data": {
            "name": "hello",
            "options": []
        }
    }
    :example:
    {
        "application_id": "XXXXXXXXXX",
        "token": "abcdefghijklmnopqrstuvwxyz",
        "data": {
            "name": "fetch",
            "options": []
        }
    }
    """
    # This can also be stored into AWS Secrets Manager and read from there.
    # For Production or public use: it's HIGHLY RECOMMENED to store this in AWS Secrets Manager.
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    print(event)
    event_body = json.loads(event["body"])
    application_id = event_body["application_id"]
    interaction_token = event_body["token"]
    command_data = event_body["data"]
    command_name = command_data["name"]

    FOLLOW_MSG_URL = (
        f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}"
    )
    headers = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}

    if command_name == "hello":
        payload = {"content": "Hello World!"}
        response = requests.post(
            FOLLOW_MSG_URL, headers=headers, data=json.dumps(payload)
        )
        if response.status_code != 200:
            print(f"Error: {response.text}")
    if command_name == "fetch":
        try:
            aws_blog_name = command_data["options"][0]["value"]
            blog_url = os.environ.get(f"{aws_blog_name.upper()}_URL")
            s3_bucket = os.environ.get("LAST_UPDATED_S3_BUCKET")

            # create s3_key
            s3_key = f"aws_rss_bot/last_updates/{aws_blog_name.upper()}_LAST_PUBLISHED_DATE.txt"

            # get the last published date from s3 -- can be async
            last_published = get_last_published_date(s3_bucket, s3_key)

            if hasattr(ssl, "_create_unverified_context"):
                ssl._create_default_https_context = ssl._create_unverified_context
            blogs = feedparser.parse(blog_url)
            if blogs.bozo:
                print(blogs.bozo_exception)
                payload = {"content": "Error fetching blogs."}
                response = requests.post(FOLLOW_MSG_URL, headers=headers, data=json.dumps(payload))
                return

            # get all the blog entries from parsed RSS FEED
            blog_posts = blogs.entries

            if last_published:
                new_blogs = list(
                    filter(
                        lambda blog: datetime.strptime(
                            blog.published, "%a, %d %b %Y %H:%M:%S %z"
                        )
                        > datetime.strptime(last_published, "%d-%m-%Y %H:%M:%S %z"),
                        blog_posts,
                    )
                )
            else:
                new_blogs = blog_posts

            if new_blogs:
                # sort new_blogs based on published date
                new_blogs.sort(
                    key=lambda blog: datetime.strptime(
                        blog.published, "%a, %d %b %Y %H:%M:%S %z"
                    )
                )
                # get the last item from list to get the max_published date
                max_published_date = datetime.strftime(
                    datetime.strptime(
                        new_blogs[-1].published, "%a, %d %b %Y %H:%M:%S %z"
                    ),
                    "%d-%m-%Y %H:%M:%S %z",
                )

                # max embeds that can be sent at once = 10 as per discord limitation.
                if len(new_blogs) > 10:
                    ini_num = 0
                    final_num = 10
                    selected_blogs = new_blogs[:final_num]
                    print("first response", len(selected_blogs), ini_num, final_num)
                    embeds = create_embeds(selected_blogs)
                    # send first response here
                    response_list = send_response(FOLLOW_MSG_URL, headers, embeds)
                    if all(response_list):
                        write_published_date(max_published_date, s3_bucket, s3_key)
                    while (
                        len(selected_blogs) >= 10
                    ):  # same interaction token can be used.
                        ini_num = ini_num + 10
                        final_num = (
                            final_num + 10
                            if final_num + 10 <= len(new_blogs)
                            else len(new_blogs)
                        )
                        selected_blogs = new_blogs[ini_num:final_num]
                        print("next response", len(selected_blogs), ini_num, final_num)
                        if selected_blogs:
                            embeds = create_embeds(selected_blogs)
                            response_list = send_response(FOLLOW_MSG_URL, headers, embeds)
                else: # when blogs <= 10
                    embeds = create_embeds(new_blogs)
                    responses = send_response(FOLLOW_MSG_URL, headers, embeds)
                    if all(responses):
                        write_published_date(max_published_date, s3_bucket, s3_key)
            else:
                payload = {"content": "No new blogs published."}
                response = requests.post(FOLLOW_MSG_URL, headers=headers, data=json.dumps(payload))
        except Exception as e:
            print(e)
            payload = {"content": "Error executing command."}
            response = requests.post(FOLLOW_MSG_URL, headers=headers, data=json.dumps(payload))
            raise e
