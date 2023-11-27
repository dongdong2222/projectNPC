
def check_if_file_exists(curr_file):
  """
  Checks if a file exists
  ARGS:
    curr_file: path to the current csv file.
  RETURNS:
    True if the file exists
    False if the file does not exist
  """
  try:
    with open(curr_file) as f_analysis_file: pass
    return True
  except:
    return False

def remove_bracket(str_with_bracket):
  if "(" in str_with_bracket:
    return str_with_bracket.split("(")[-1][:-1]


def convert_address_to_dict(ad_str):
  ad_strs = ad_str.split(':')
  ad_dict = {}
  ad_dict['world'] = ad_strs[0]
  ad_dict['sector'] = ad_strs[1]
  ad_dict['arena'] = ad_strs[2]
  ad_dict['object'] = ad_strs[3]
  return ad_dict
