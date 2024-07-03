#OpenAI-Beta: assistants=v2
from flask import Flask, request, jsonify
import openai
import json
import requests
import Flight_info as fi

app = Flask(__name__)
client = openai.OpenAI(api_key = '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')

@app.route('/flight', methods=['GET'])
def handle_request():
    
    info_dict = {'code': request.args.get('departure'),
                 'type': 'departure',
                 'date_from': request.args.get('date_from'),
                 'date_to': request.args.get('date_to'),
                 'airline_iata': request.args.get('airline'),
                 'flight_num': request.args.get('flight_num')
                }
    # Create a assistant that can help to extract flight information and generate to JSON format
    # extract_assistant = client.beta.assistants.create(
    #   name="extract assistant",
    #   instructions=f"You are good at extracting the flight number and delay information from the prompt the user sends to you \
    #   and you can reply a string with json format. If prompt does not contain enough flight information, please reply and let them provide flight information. \
    #   ",
    #   model="gpt-3.5-turbo",

    #   response_format={ "type": "json_object" }
    # )

    thread = client.beta.threads.create()

    # client_prompt = "My flight with flight number CX 888 had delayed for 5 hours on June 28 2024, what compensation can I get?"

    # message = client.beta.threads.messages.create(
    #   thread_id=thread1.id,
    #   role="user",
    #   content = client_prompt + " Please output json format like this: \n{{\"carrierCode\": \"CX\",\"flightNumber\": \"813\", \"scheduledDepartureDate\": \"2024-06-26\", \"delay\": \"4 hours\"}}"
    # )
    # return jsonify({"message": "Data received", "data": data})

    # run = client.beta.threads.runs.create_and_poll(
    #   thread_id=thread1.id,
    #   assistant_id=extract_assistant.id,
    #   instructions="Please address the user as Andy Zhang. The user has a premium account."
    # )

    # extracted_info = ''
    # if run.status == 'completed': 
    #   messages= client.beta.threads.messages.list(
    #     thread_id=thread1.id
    #   )
    #   # print(messages)
    #   extracted_info = messages.data[0].content[0].text.value.strip()
    # else:
    #   print(run.status)
    #   exit

    # info_dict = {}

    # try:
    #     info_dict = json.loads(extracted_info)
    #     print(info_dict)
    # except json.JSONDecodeError:
    #     # return fail info
    #     print("error:" + "Failed to parse the extracted information")
    #     exit


    flight_dict = fi.get_flight_info(info_dict)

        # delay_info ={
        #         'departure': flight["departure"]["iataCode"],
        #         'arrival': flight["arrival"]["iataCode"],
        #         'delay': flight["departure"]["delay"],
        #         "scheduledTime": flight["departure"]["scheduledTime"],
        #         "actualTime": flight["departure"]["actualTime"]
        #     }

    # flight_prompt = (
    #       "Extract the following information from the given API response and return it as a JSON object:\n\n"
    #       "1. Flight number\n"
    #       "2. Scheduled departure date\n"
    #       "3. Departure airport code\n"
    #       "4. Arrival airport code\n"
    #       "5. Scheduled departure time\n"
    #       "6. Scheduled arrival time\n"
    #       "7. Flight duration\n"
    #       "8. Aircraft type\n\n"
    #       f"API response:\n{json.dumps(flight_dict)}\n\n"
    #       "Example output:\n"
    #       "{\n"
    #       "  \"flight_number\": \"CX 888\",\n"
    #       "  \"scheduled_departure_date\": \"2024-06-28\",\n"
    #       "  \"departure_airport_code\": \"HKG\",\n"
    #       "  \"arrival_airport_code\": \"YVR\",\n"
    #       "  \"scheduled_departure_time\": \"2024-06-28T00:45+08:00\",\n"
    #       "  \"scheduled_arrival_time\": \"2024-06-27T21:50-07:00\",\n"
    #       "  \"flight_duration\": \"PT12H5M\",\n"
    #       "  \"aircraft_type\": \"359\"\n"
    #       "}"
    #       )

    flight_info_assistant = client.beta.assistants.create(
      name="flight assistant",
      instructions="You are good at answering the delay time (in minutes) based on the given json data",
      model="gpt-3.5-turbo"
    )

# thread = client.beta.threads.create()

    flight_prompt = ("Given the flight information in json format, please answer if the flight is delay and how long.\n\n"
                     "Answer should include the departure, arrival, the scheduled time, actualTime and the delay duration.\n"
                     f"flight information in json object:\n{json.dumps(flight_dict)}\n\n"
    )

    message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content = flight_prompt
    )

# message = client.beta.threads.messages.create(
#   thread_id=thread1.id,
#   role="user",
#   content="My flight with flight number CX 888 had delayed for 5 hours, what compensation can I get?"
# )

    run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id,
      assistant_id=flight_info_assistant.id,
      instructions="The user has a premium account."
    )

    delay_info = ''
    if run.status == 'completed': 
      messages= client.beta.threads.messages.list(
        thread_id=thread.id
      )
      # print(messages)
      delay_info = messages.data[0].content[0].text.value.strip()
      # print(delay_info)
    else:
      # print(run.status)
      exit

    # return delay_info


    # info_dict = {}

    # try:
    #     # info_dict = json.loads(flight_info)
    #     print(info_dict)
    # except json.JSONDecodeError:
    #     # return fail info
    #     print("error:" + "Failed to parse the extracted information")
    #     exit

    policy_assistant = client.beta.assistants.create(
      name="Compensation Policy Assistant",
      instructions="You are an expert with a thorough understanding of compensation policies for flight delays, well-versed in the policies of different countries and regions. Based on the policy files I provided to you, answer questions about compensation of flight delays. Does not need to contain source in your output",
      model="gpt-4o",
      tools=[{"type": "file_search"}],
    )

    vector_store = client.beta.vector_stores.create(
      name="Compensation Policy",
      file_ids=['file-fZdgcNF7U7NXpvuMSgx638U9', 'file-wohCGaemJwkiTCGhgUjRj755']
    )

    policy_assistant = client.beta.assistants.update(
      assistant_id=policy_assistant.id,
      tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    # Use the create and poll SDK helper to create a run and poll the status of
    # the run until it's in a terminal state.

    message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content = delay_info + '\nCan I get compensation based on the information I provide? Please only provide policies regard departure. Thanks'
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=policy_assistant.id
    )

    delay_info = ''
    if run.status == 'completed': 
        messages= list(client.beta.threads.messages.list(
          thread_id=thread.id,
          run_id=run.id
        ))
        print(messages)
        delay_info = messages[0].content[0].text.value
        # print(delay_info)
    else:
        # print(run.status)
        exit

    # messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    # message_content = messages[0].content[0].text
    # # messages.data[0].content[0].text.value.strip()
    # print(messages)

    # print(message_content.value)
    # print("\n".join(citations))

    return delay_info



# if run.status == 'completed': 
#   messages= client.beta.threads.messages.list(
#     thread_id=thread1.id
#   )
#   # message = client.beta.threads.messages.retrieve(
#   # thread_id=thread.id,
#   # message_id=messages
#   # )
#   print(messages.data[0].content[0].text.value)

# else:
  # print(run.status)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(port=8000, host="0.0.0.0")
