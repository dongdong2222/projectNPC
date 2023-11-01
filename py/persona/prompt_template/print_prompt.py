

def print_run_prompts(prompt_template=None,
                      persona=None,
                      gpt_param=None,
                      prompt_input=None,
                      prompt=None,
                      output=None):
  print (f"=== {prompt_template}")
  print ("~~~ persona    ---------------------------------------------------")
  print (persona.name, "\n")
  print ("~~~ gpt_param ----------------------------------------------------")
  print (gpt_param, "\n")
  print ("~~~ prompt_input    ----------------------------------------------")
  print (prompt_input, "\n")
  print ("~~~ prompt    ----------------------------------------------------")
  print (prompt, "\n")
  print ("~~~ output    ----------------------------------------------------")
  print (output, "\n")
  print ("=== END ==========================================================")
  print ("\n\n\n")