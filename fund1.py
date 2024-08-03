import xml.etree.ElementTree as ET
import pandas as pd

# Parse the XML file
tree = ET.parse('data.xml')
root = tree.getroot()

# Extracting data for DataFrame creation
def extract_issues_data(root):
    data = []
    for issue in root.findall('.//Issues/Issue'):
        issue_data = {
            'ID': issue.get('ID'),
            'Type': issue.get('Type'),
            'Desc': issue.get('Desc'),
            'Order': issue.get('Order')
        }
        for issueID in issue.findall('.//IssueID'):
            issue_data[issueID.get('Type')] = issueID.text
        exchange = issue.find('.//Exchange')
        if exchange is not None:
            issue_data['ExchangeCode'] = exchange.get('Code')
            issue_data['ExchangeCountry'] = exchange.get('Country')
            issue_data['Exchange'] = exchange.text
        most_recent_split = issue.find('.//MostRecentSplit')
        if most_recent_split is not None:
            issue_data['MostRecentSplitDate'] = most_recent_split.get('Date')
            issue_data['MostRecentSplitValue'] = most_recent_split.text
        
        data.append(issue_data)
    return data

issues_data = extract_issues_data(root)

# Convert to DataFrame
df_issues = pd.DataFrame(issues_data)

# print(df_issues.to_csv('fund.csv'))

# # Display the DataFrame
# import ace_tools as tools; tools.display_dataframe_to_user(name="Issues DataFrame", dataframe=df_issues)
print(df_issues)


import xml.etree.ElementTree as ET
import pandas as pd

# Parse the XML file
tree = ET.parse('data.xml')
root = tree.getroot()

# Extracting ratio data for DataFrame creation
def extract_ratios_data(root):
    data = []
    for group in root.findall('.//Ratios/Group'):
        group_id = group.get('ID')
        for ratio in group.findall('.//Ratio'):
            ratio_data = {
                'GroupID': group_id,
                'FieldName': ratio.get('FieldName'),
                'Type': ratio.get('Type'),
                'Value': ratio.text
            }
            data.append(ratio_data)
    return data

ratios_data = extract_ratios_data(root)

# Convert to DataFrame
df_ratios = pd.DataFrame(ratios_data)

print(df_ratios)
