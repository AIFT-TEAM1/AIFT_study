from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("kiwoom 실행") 

        ########이벤트 루프 모음########
        self.login_event_loop = None
        self.detail_account_info_event_loop = None
        self.detail_account_info_event_loop2 = None
        ###############################
        
        #####변수 모음########
        self.account_num = None
        ######################

        ####계좌관련 변수######
        self.use_money = 0
        self.use_money_percent = 0.5



        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info() #예수금 가져오는 것
        self.detail_account_mystock() #계좌평가 잔고 내역 요청

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)
    
    def login_slot(self, errCode):
        print(errors(errCode)) #errCode == 0 올바르게 연결

        self.login_event_loop.exit()
    
    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    ####내 정보 가져오기
    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCNO")

        self.account_num = account_list.split(';')[0]

        print("나의 보유 계좌번호 %s" % self.account_num)#8034722411

    def detail_account_info(self):
        print("예수금 요청오는 부분")

        self.dynamicCall("SetInputValue(String, String)","계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)","비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)","비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)","조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "opw00001", "0", "2000")

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()
    
    def detail_account_mystock(self, sPrevNext = '0'):
        print("계좌평가 잔고내역 요청")
        
        self.dynamicCall("SetInputValue(String, String)","계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)","비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)","비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)","조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, "2000")

        self.detail_account_info_event_loop2 = QEventLoop()
        self.detail_account_info_event_loop2.exec_()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPreNext):
        '''
        tr 요청을 받는 구역 
        sScrNo: 스크린번호
        sRQName: 내가 요청했을 때 지은 이름
        sTrCode: 요청id, tr 코드
        sPrevNext: 다음 페이지가 있는지 
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            print("예수금 %s" % type(deposit))
            print("예수금 형변환 %s"%int(deposit))

            self.use_money = int(deposit) * self.use_money_percent
            self.use_money = self.use_money / 4

            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금가능금액 %s" % type(ok_deposit))
            print("출금가능금액 %s" % int(ok_deposit))

            self.detail_account_info_event_loop.exit()
        
        if sRQName == "계좌평가잔고내역요청":

            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)

            print("총매입금액 %s" % total_buy_money_result)

            total_profit_loss_rate_result = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")
            print("총수익률(%%) : %s" % total_profit_loss_rate_result)


            rows = self.dynamicCall("GetRepeatCnt(Qstring, Qstring)", sTrCode, sRQName)
            cnt = 0

            for i in range(rows):
                code = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)",sTrCode, sRQName, cnt, "종목번호")
                code = code.strip()[1:] # A2310 -> 2310

                code_nm = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)",sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)",sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)",sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)",sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)",sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)",sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)",sTrCode, sRQName, i, "매매가능수량")



                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())


            self.detail_account_info_event_loop2.exit()
