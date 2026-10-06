# email_script
I want you to program me the following script in python.
# open xlsx file. save SFA Emails sheet as emails df, and Library sheet as Library df.

#Create subset dataframe of emails df called filtered_emails of only records where Status column has a value of 'Match' and yes_flag column includes the value 'y'. This df should be including all other columns of course.
#Now loop through every record of filtered_emails, store that record's values for "Email Address", "First Name" and "Last Name" and "match_institution" column.
# for every loop, it should look inside the Library dataframe for a match. The library dataframe's columns of interest are InstitutionName, StandardInvestigatorFirstName, StandardInvestigatorLastName and Email Match from TF

# for example: the First Name value should match StandardInvestigatorFirstName, 
# match_institution should match InstitutionName, 
# Last Name should match StandardInvestigatorLastName 
# For algorithmic efficiency, i highly recommend matching first on InstitutionName by creating a dataframe of all records in library that have the same InstitutionName as match_institution.
#From there you can match on the first and last names.
# Once you find the record or records (multiple is acceptable) inside the Library dataframe, fill it or their 'Email Match from TF' column with the value you captured earlier from the filtered_email's 'Email Address' column.



=IF(TRIM(U2)<>"", TRIM(U2), IF(TRIM(X2)<>"", TRIM(X2), ""))
