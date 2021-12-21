# Music-Theray-Documentation

Video Demo: https://youtu.be/0lNZhjQuR9g

## Summary:

A web app that lets the therapist 1) input client info including goals and objectives 2) document session outcomes 
3) dynamically generate documentation reports 4) with a click of a button, send all client families dynamically generated reports and emails

## How to Use:

Please remember your registration info as this app doesn't have a change passwork function yet.
On the New Client page, whenever writing goals, please make sure to start the sentence with "To"
Please make sure to follow the prompt when entering dates, enter year with four digits, enter month without "0"s
Please be careful with Email Report function. This function will send the reports from the specified month to ALL clients who have a caregiver email input by you.
Please contact me for any questions or problems you may run into. 
If data analysis is needed, please contact me for graphs, analysis and other things that can be easily done with SQL data and python libraries.

## Description:

🛠️ Tools and languages used: Python, Flask, MySQL

🤔 Rationale for Creating This Project: I was getting exhausted having to manually put in documentation data using Microsoft Word. 
There were too many times I had to copy and paste, rename, delete, only to move onto documentating for the next month. 
Sending monthly reports to caregivers with custimized reports and messages were even more excruiciating. 
With this web app, I can save myself so much time and clicks.

💆‍♀️ Challenges I Faced: The first big challenge was how to set up the relational database: 
every client has different goals and objectives and their outcomes need to be documented under each objective accordingly, 
indexed by date for data pulling in generating the reports. MySQL syntax was also different from SQLite and that took getting used to.
Then having the program be flexible about the number of goals and objectives each client can have, 
as some of them have none and we only rely on narrative notes. 
I am still trying to clean up the code as I have time and create more functions such as update goals and objectives 
which is integral to therapists. I would also like to one day create API for therapist authentication.

📕 Libraries That Helped: FPDF to generate pdf reports smtplib to send emails 
Thank you to this youtube channel that significantly helped with my learning curve with FPDF 
and developing the professional-looking template for the tables: https://www.youtube.com/watch?v=q70xzDG6nls

