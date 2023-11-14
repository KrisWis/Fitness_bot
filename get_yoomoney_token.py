from yoomoney import Authorize

Authorize(
      client_id="404A96B3677E5AC84F4523BD23A72A83EA6B368E145F0270267A0908B8552E23",
      redirect_uri="https://yoomoney.ru/myservices/new",
      scope=["account-info",
             "operation-history",
             "operation-details",
             "incoming-transfers",
             "payment-p2p",
             "payment-shop",
             ]
      )