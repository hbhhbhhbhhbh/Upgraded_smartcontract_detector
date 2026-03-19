"# Upgraded_smartcontract_detector"

1. methon of get sorce code of samrt contract
   first get a free api key in etherscan in link https://etherscan.io/apis
   when you get your api, replace get_sourcecode.py API_KEY value.

  visit https://www.google.com/search?q=https://etherscan.io/contractsVerified to find contracts address, copy address you want replace them in        verified_contract value.
  run get_sourcecode.py, all source code download.
  in command shell, run command 'npm install -g sol-merger',
  
  if source code is multi-files, you can  flatten it, run command ' sol-merger main_sol_file.sol way_flatten_file_placed '
