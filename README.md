# Demo

aws lambda add-permission --function-name cmtr-bd916154-iam-lp-lambda \
  --principal apigateway.amazonaws.com \
  --statement-id unique-statement-id-1 \
  --action lambda:InvokeFunction \
  --source-arn arn:aws:apigateway:eu-central-1::/restapis/cmtr-bd916154-iam-lp-apigwv2_api/*/*/* \
  --source-account 196241772369

