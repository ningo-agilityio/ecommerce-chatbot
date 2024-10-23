# 💬 Chatbot template

A simple Streamlit app that shows how to build a chatbot using OpenAI's GPT-3.5.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### How to run it on your own machine
1. Add file credentials for Google Shopping API into **chatbot/assets** folder
To create credentials for Google Shopping API:

a. Create a Project in Google Cloud Console:
   - Go to Google Cloud Console.
   - Create a new project.
   - Enable the Content API for Shopping from the API Library.

b. Set Up OAuth2 or API Key:
- For secure access to the Google Shopping API, set up OAuth2 credentials (recommended).
- Alternatively, you can use an API key for read-only access.

c. Navigate to IAM & Admin → Service Accounts:

- On the left-hand menu, click on IAM & Admin.
- From the dropdown, choose Service Accounts.
- Create or Select a Service Account
- After selecting or creating the service account, click on the Keys tab.
- Click Add Key → Create new key
- Choose JSON as the key type.
- Download the JSON Key
2. Create Merchant Id

a. To retrieve the merchant id, please go to [Merchant center](https://merchants.google.com/mc/overview?a=5444340493&src=ome) and register one.
b. Navigate to Users Section:

   + Go to Settings → People and access. Invite the Service Account:
   + Click the plus (+) button to invite a new user.
   + Enter the service account's email address (which is in your service account JSON file under the "client_email" field, e.g., your-service-account@your-project-id.iam.gserviceaccount.com).
   + Set the role to Admin or Standard depending on the access you want to provide. 
c. Create product on your merchant to return valid response.
d. Then fill the id up into .env file

2. Add **.env** with provided variables keys in **.env.sample**
3. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

4. To activate conda environment, from root folder:

   ```
   $ conda activate ecommerce-chatbot
   ```

5. To run the app, from root folder:

   ```
   $ streamlit run streamlit_app.py
   ```

6. To run test:
- For e-commerce app:
   ```
   $ cd tests/e-commerce
   $ npm run test
   ```
- For translation app:
   ```
   $ cd tests/translation
   $ npm run test
   ```

7. Run Fast api:
   ```
   $ uvicorn app.main:app --reload
   ```

**Notes**: Some questions to test chatbot:
- Tell me about order process
- Tell me about faqs
- Give me price of Black Forest Cake
- Provide me information about Mini Cake with Chocolate
- What is LangChain?
- Guide me how to order Mini Cake
- What is the price of a Black Forest Cake and what is the return policy for this item?