import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

    """
    This code fetches current gas prices from a list of GasBuddy station URLs, 
    stores the data in a CSV file, and allows for filtering the data by date. 
    It retrieves prices for regular, midgrade, and premium fuel, formats the data for email, 
    and sends an email with the gas price information to specified recipients. 
    The code includes functions for data retrieval, filtering, formatting, and email sending.

    get_gas_prices(url):
        Fetches gas prices from the provided URL.

        Parameters:
        url (str): The URL of the gas station page.

        Returns:
        dict: A dictionary with gas prices for regular, midgrade, and premium fuel types.

    filter_for_day(file_path, target_date):
        Filters gas prices for a specific day from a CSV file.

        Parameters:
        file_path (str): The path to the CSV file containing gas price data.
        target_date (str): The date to filter the gas prices for (format: YYYY-MM-DD).

        Returns:
        DataFrame: A DataFrame containing the filtered gas price data for the target date.

    format_data_as_text(df):
        Formats the gas price data as a text string.

        Parameters:
        df (DataFrame): A DataFrame containing the gas price data.

        Returns:
        str: A formatted string containing the gas price information.

    send_email(subject, body, to_emails):
        Sends an email with the provided subject and body to the specified recipients.

        Parameters:
        subject (str): The subject of the email.
        body (str): The body content of the email.
        to_emails (list): A list of recipient email addresses.
    """


if __name__ == "__main__":
    '''
    place the functions in a main method to run at a scheduled time using WindowsTaskScheduler 
    #OR just delete the main method and run the functions as desired
    '''
    def get_gas_prices(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        #adding the headers parameter allows the request to look "more human" and actually return text
        response = requests.get(url, headers=headers)
        
        if response.status_code == 403:
            print(f"Access forbidden for URL: {url}")
            return {}
    
        soup = BeautifulSoup(response.content, 'html.parser')
    
        prices = {}
        try:
            '''
            The current prices are stored along with historical pricing 
            To get current prices, find the fuel price that is displayed 
            *NOTE regular, midgrade and premium are really the first, second and third prices
            that the script finds. If the station only offers two gas types or offers more than 3
            the prices will not be named correctly. 
            '''
            price_elements = soup.find_all('div', {'class': 'GasPriceCollection-module__priceDisplay___1pnaL'})
            if len(price_elements) >= 3:
                prices['regular'] = price_elements[0].find('span', {'class': 'FuelTypePriceDisplay-module__price___3iizb'}).text.strip().replace('$', '')
                prices['midgrade'] = price_elements[1].find('span', {'class': 'FuelTypePriceDisplay-module__price___3iizb'}).text.strip().replace('$', '')
                prices['premium'] = price_elements[2].find('span', {'class': 'FuelTypePriceDisplay-module__price___3iizb'}).text.strip().replace('$', '')
        except Exception as e:
            print(f"Error parsing prices from URL: {url} - {e}")
    
        return prices
    

    station_data = [
        {'url': 'https://www.gasbuddy.com/station/72802', 'nickname': 'Fastrak Broadway', 'location': 'Portland'},
        {'url': 'https://www.gasbuddy.com/station/105460', 'nickname': 'Fastrak Fremont', 'location': 'Portland'},
        {'url': 'https://www.gasbuddy.com/station/29803', 'nickname': 'Shell 33rd Broadway', 'location': 'Portland'},
        
        {'url': 'https://www.gasbuddy.com/station/41005', 'nickname': 'Fastrak Milwaukie', 'location': 'Milwaukie'},
        {'url': 'https://www.gasbuddy.com/station/76591', 'nickname': 'Safeway Milwaukie', 'location': 'Milwaukie'},
        {'url': 'https://www.gasbuddy.com/station/76591', 'nickname': 'SpaceAge Milwaukie', 'location': 'Milwaukie'},
        
        {'url': 'https://www.gasbuddy.com/station/10847', 'nickname': 'Roadrunner', 'location': 'Scappoose'},
        {'url': 'https://www.gasbuddy.com/station/14297', 'nickname': 'Fred Meyer Scappoose', 'location': 'Scappoose'},
        {'url': 'https://www.gasbuddy.com/station/32005', 'nickname': '76 Scappoose', 'location': 'Scappoose'},
        {'url': 'https://www.gasbuddy.com/station/32007', 'nickname': 'Shell Scappoose', 'location': 'Scappoose'}
        
    
        # Add as many stations as you would like
    ]
    
    data = []
    date = datetime.now().strftime('%Y-%m-%d')
    
    # Loop through each station data and get prices
    for station in station_data:
        prices = get_gas_prices(station['url'])
        prices['date'] = date
        prices['station_nickname'] = station['nickname']
        prices['location'] = station['location']
        data.append(prices)
    
    new_df = pd.DataFrame(data)
    # print(new_df)
    # Filepath to the CSV file to store the gas prices
    file_path = 'gas_prices.csv'
    
    if os.path.exists(file_path):
        # If the file exists, append the new data without writing the header
        new_df.to_csv(file_path, mode='a', header=False, index=False) #mode = 'a' and header = False to append data
        print("Gas prices have been appended to gas_prices.csv")    
    else:
        # If the file does not exist, create it and write the header
        new_df.to_csv(file_path, mode='w', header=True, index=False)
        print("Creating gas_prices.csv file")
    
    def filter_for_day(file_path, target_date):
        if not os.path.exists(file_path):
            print(f"No data file found at {file_path}")
            return None
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        day_df = df[df['date'] == target_date]
    
        return day_df
    
    target_date = datetime.now().strftime('%Y-%m-%d')
    day_df = filter_for_day(file_path, target_date)
    
    if day_df is not None and not day_df.empty:
        print("Filtered data for the target date:")
        print(day_df)
    else:
        print("No data available for the target date.")
    
    def format_data_as_text(df):
        text = f"Gas Prices for {target_date}:\n\n"
        for index, row in df.iterrows():
            text += f"Station: {row['station_nickname']} ({row['location']})\n"
            text += f"Regular: ${row['regular']}\n"
            text += f"Midgrade: ${row['midgrade']}\n"
            text += f"Premium: ${row['premium']}\n"
            text += "\n"
        return text
    
    if day_df is not None and not day_df.empty:
        email_body = format_data_as_text(day_df)
        print("Formatted data for email:")
        print(email_body)
    else:
        email_body = "No data available for the target date."
    
    def send_email(subject, body, to_emails):
        # Email credentials
        smtp_server = 'smtp.gmail.com'  # Replace with your SMTP server
        smtp_port = 587  # Replace with your SMTP port (usually 587 for TLS)
        smtp_user = 'senderuser@gmail.com'  # Replace with your email address
        smtp_password = 'senderpassword'  # Replace with your email password
    
        smtp = smtplib.SMTP('smtp.gmail.com', 587) 
        smtp.ehlo() 
        smtp.starttls() 
    
        # Login with your email and password 
        smtp.login(smtp_user, smtp_password)
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject
    
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
    
        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, to_emails, text)
        server.quit()
    
        print("Email sent successfully.")
    
    # Recipients list
    recipients = ['recipientuser@gmail.com']
    
    # Send email with the formatted data
    send_email(
        subject=f"Gas Prices for {target_date}",
        body=email_body,
        to_emails=recipients
    )
    
    
    
