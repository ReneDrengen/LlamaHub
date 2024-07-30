import os
from typing import Generator, List

import pytest
from llama_index.core.schema import NodeRelationship, RelatedNodeInfo, TextNode
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.vector_stores.wordlift import WordliftVectorStore
from wiremock.client import *
from wiremock.constants import Config
from wiremock.testing.testcontainer import wiremock_container, WireMockContainer
from wordlift_client import Configuration

KEY = "key43245932904328493223"


@pytest.fixture(scope="session")
def node_embeddings() -> List[TextNode]:
    embedding = [
        -0.02409953996539116,
        0.007545656058937311,
        -0.010837538167834282,
        -0.015247111208736897,
        0.020510902628302574,
        0.02260207198560238,
        0.03624352440237999,
        -0.02312600426375866,
        0.03509214147925377,
        0.009039043448865414,
        -0.04192536696791649,
        0.0646052435040474,
        0.05423989146947861,
        -0.006866314448416233,
        0.032361097633838654,
        -0.003253199392929673,
        0.05170004814863205,
        -0.054772719740867615,
        0.008567743934690952,
        -0.008800626732409,
        -0.035540562123060226,
        -0.0036080495920032263,
        -0.012353642843663692,
        -0.049400247633457184,
        0.0490705706179142,
        -0.017110642045736313,
        0.0434158556163311,
        0.0047591072507202625,
        -0.04901169613003731,
        0.04313654080033302,
        0.08862752467393875,
        -0.0305459126830101,
        0.031628116965293884,
        -0.0023637129925191402,
        -0.0062087783589959145,
        0.016893181949853897,
        0.02979143150150776,
        0.016508951783180237,
        0.02346094138920307,
        0.0370299331843853,
        -0.022708870470523834,
        -0.040380027145147324,
        0.027732161805033684,
        -0.03321043401956558,
        0.028203414753079414,
        -0.03547737002372742,
        -0.003607464488595724,
        -0.011886986903846264,
        0.08876273781061172,
        -0.035582806915044785,
        0.01728527806699276,
        0.033559445291757584,
        0.03006189689040184,
        -0.02276725322008133,
        -0.02573985420167446,
        0.018779633566737175,
        0.018232546746730804,
        0.04365724325180054,
        0.019853554666042328,
        -0.056149423122406006,
        -0.040290556848049164,
        0.055537160485982895,
        0.01000349409878254,
        0.042989231646060944,
        0.06469859182834625,
        -0.07268784195184708,
        0.029832176864147186,
        -0.00694637605920434,
        -0.019039496779441833,
        -0.028887171298265457,
        0.0611429437994957,
        -0.07661744952201843,
        0.008372906595468521,
        0.07736742496490479,
        0.01697900891304016,
        0.00455197598785162,
        -0.01660764403641224,
        0.013384402729570866,
        0.016262754797935486,
        0.04430804401636124,
        0.05316875874996185,
        -0.017527703195810318,
        -0.015531433746218681,
        0.02427724562585354,
        0.06978478282690048,
        -0.0215159859508276,
        -0.0015113558620214462,
        -0.0005745171220041811,
        -0.058096420019865036,
        0.06534607708454132,
        0.09807957708835602,
        0.03466407209634781,
        0.02070295810699463,
        0.06667006760835648,
        0.008454645052552223,
        0.004790779203176498,
        -0.0021362053230404854,
        0.012438371777534485,
        -0.025263242423534393,
        0.04503288492560387,
        -0.014884737320244312,
        -0.009326054714620113,
        -0.03726727515459061,
        -0.003038907190784812,
        0.045574598014354706,
        0.02176540531218052,
        -0.022943837568163872,
        0.03223365545272827,
        -0.0231216698884964,
        -0.008260810747742653,
        -0.0838012844324112,
        -0.0041016764007508755,
        -0.019858187064528465,
        -0.025245968252420425,
        -0.08231323212385178,
        -0.0008271003025583923,
        0.06744734942913055,
        -0.022615060210227966,
        -0.036366865038871765,
        -0.007173497695475817,
        0.023905375972390175,
        -0.026212558150291443,
        0.008525801822543144,
        0.05790192261338234,
        0.03967795893549919,
        -0.019248196855187416,
        -0.03145810589194298,
        -0.06143287941813469,
        -0.025088703259825706,
        0.008470161817967892,
        -0.019712727516889572,
        0.0201752707362175,
        -0.024380167946219444,
        -0.048689160495996475,
        0.030698394402861595,
        0.06519214808940887,
        0.006988975685089827,
        -0.030256111174821854,
        0.015067224390804768,
        -0.009249436669051647,
        0.005610473453998566,
        0.030035214498639107,
        0.0062820687890052795,
        -0.01272163912653923,
        0.0031057705637067556,
        -0.08999253064393997,
        0.03721488639712334,
        -0.028286410495638847,
        -0.041241131722927094,
        -0.011454920284450054,
        -0.024434737861156464,
        0.012364787049591541,
        0.01152063999325037,
        0.013034306466579437,
        -0.015703829005360603,
        -0.07446613907814026,
        -0.035228293389081955,
        0.029677776619791985,
        -0.0008637132123112679,
        0.03882776200771332,
        -0.03331062197685242,
        0.06260097771883011,
        -0.03643746301531792,
        0.03024205192923546,
        -0.04027588292956352,
        -0.006302598863840103,
        -0.03876963630318642,
        0.022751253098249435,
        0.05228758603334427,
        -0.00650898227468133,
        0.00784189160913229,
        -0.02789650298655033,
        -0.03584962338209152,
        -0.03039231151342392,
        0.005157549399882555,
        0.038540806621313095,
        0.016989191994071007,
        0.002693451475352049,
        0.03680325672030449,
        -0.02772810310125351,
        0.04701118916273117,
        0.00428611459210515,
        0.008383968845009804,
        0.01370905339717865,
        -0.03272991627454758,
        0.025361433625221252,
        0.07640355080366135,
        -0.09241847693920135,
        -0.018185008317232132,
        -0.0033845037687569857,
        0.016245491802692413,
        -0.010160512290894985,
        -0.01563146524131298,
        -0.05825433135032654,
        0.01485800463706255,
        -0.012620965018868446,
        0.012889757752418518,
        -0.07174727320671082,
        0.0036001859698444605,
        0.0003497107536531985,
        -0.010015580803155899,
        -0.026276255026459694,
        -0.054649949073791504,
        0.0178300142288208,
        -0.03058459609746933,
        -0.0046766879968345165,
        0.02828553318977356,
        0.004914792720228434,
        0.006221550516784191,
        0.02017192542552948,
        0.06884320825338364,
        -0.005684717558324337,
        -0.03233734890818596,
        0.028631558641791344,
        -0.037736676633358,
        0.012628731317818165,
        0.011251229792833328,
        -0.01216588169336319,
        -0.0449829027056694,
        0.05112060159444809,
        0.0321006216108799,
        0.004842250142246485,
        -0.028930027037858963,
        -0.03781994432210922,
        0.027888713404536247,
        -0.0020639710128307343,
        -0.012764016166329384,
        0.001849374850280583,
        -0.06090773642063141,
        0.024058688431978226,
        -0.07892243564128876,
        -0.022651061415672302,
        0.03663799911737442,
        -0.015678945928812027,
        0.034871794283390045,
        0.02377290651202202,
        0.01880395971238613,
        0.005291060544550419,
        0.06636939197778702,
        0.07682432979345322,
        0.06366447359323502,
        0.045753464102745056,
        -0.021396778523921967,
        -0.06412482261657715,
        -0.022975077852606773,
        -0.015396900475025177,
        -0.01382171455770731,
        0.04801446571946144,
        -0.044695984572172165,
        0.010728792287409306,
        -0.013164067640900612,
        -0.06426115334033966,
        0.016030244529247284,
        0.01712176389992237,
        0.003342918585985899,
        -0.024401094764471054,
        -0.04742956534028053,
        0.05057492479681969,
        -0.06447580456733704,
        0.003736401442438364,
        -0.0038414313457906246,
        -0.044975876808166504,
        0.01563481241464615,
        -0.0513794831931591,
        0.03116164542734623,
        0.05475221946835518,
        -0.018825948238372803,
        -0.05825172737240791,
        0.026944046840071678,
        -0.01748691312968731,
        -0.015295912511646748,
        0.041276704519987106,
        0.06435948610305786,
        0.057869717478752136,
        0.007085255812853575,
        -0.0016246287850663066,
        -0.049611661583185196,
        -0.02173301763832569,
        -0.03379219397902489,
        -0.010483022779226303,
        -0.04382925480604172,
        -0.019825980067253113,
        -0.028733380138874054,
        0.00799755472689867,
        -0.010613085702061653,
        0.03142009675502777,
        0.0993402749300003,
        0.013524055480957031,
        0.04996125027537346,
        -0.05237795040011406,
        0.00459002610296011,
        0.03747300058603287,
        -0.007390610408037901,
        0.03675704449415207,
        0.028937028720974922,
        0.0490734800696373,
        0.07018966227769852,
        0.02625582180917263,
        -0.012768297456204891,
        -0.017309138551354408,
        0.009925411082804203,
        0.002874719677492976,
        -0.03868229687213898,
        -0.011665035039186478,
        0.016460483893752098,
        -0.016710275784134865,
        0.026092402637004852,
        -0.029528427869081497,
        0.027799755334854126,
        0.00869158748537302,
        0.00814155675470829,
        0.025196386501193047,
        0.010806374251842499,
        0.007144266739487648,
        0.009723981842398643,
        0.040421262383461,
        -0.014507091604173183,
        0.00026819604681804776,
        0.04148963838815689,
        -0.011153719387948513,
        0.011801899410784245,
        -0.04976220428943634,
        0.01822030358016491,
        -0.022088022902607918,
        0.010638813488185406,
        0.050233982503414154,
        0.03569936379790306,
        0.024639304727315903,
        0.04990961775183678,
        0.006694141309708357,
        0.03368678316473961,
        0.05511782318353653,
        0.006736745126545429,
        -0.03352257236838341,
        0.06660161167383194,
        0.012697044759988785,
        -0.0414629764854908,
        0.00029493123292922974,
        -0.010526367463171482,
        -0.015528022311627865,
        -0.024239003658294678,
        0.014093346893787384,
        -0.05118495970964432,
        -0.04236882925033569,
        0.026792580261826515,
        -0.04413650929927826,
        -0.008981052786111832,
        0.02730277180671692,
        0.06500429660081863,
        0.011842386797070503,
        -0.005152833182364702,
        -0.011248798109591007,
        0.0014251028187572956,
        -0.058844491839408875,
        -0.03179366886615753,
        0.014862962067127228,
        0.0031557243783026934,
        0.006256013177335262,
        0.022348832339048386,
        0.018381774425506592,
        0.05182422697544098,
        -0.007802502252161503,
        0.027966707944869995,
        -0.015043427236378193,
        0.06696246564388275,
        0.06933777779340744,
        0.06229571998119354,
        0.025468071922659874,
        0.04187721014022827,
        0.030144240707159042,
        -0.04005308449268341,
        0.018866809085011482,
        -0.011857784353196621,
        0.028774423524737358,
        0.0008001378737390041,
        0.051755640655756,
        -0.0763072744011879,
        -0.035968881100416183,
        -0.06542054563760757,
        -0.01490574050694704,
        0.03574415668845177,
        0.008126146160066128,
        0.02864741161465645,
        -0.00003158819890813902,
        0.022258171811699867,
        0.009770577773451805,
        -0.044916730374097824,
        -0.07808850705623627,
        0.0390549972653389,
        -0.01499694213271141,
        0.007959951646625996,
        -0.005930764134973288,
        -0.02100251242518425,
        -0.029872389510273933,
        -0.012773459777235985,
        -0.043038900941610336,
        0.04595667123794556,
        -0.06141292303800583,
        0.03035324439406395,
        0.00792359933257103,
        -0.020943107083439827,
        0.02207357995212078,
        0.011123895645141602,
        0.03734105825424194,
        -0.010610148310661316,
        -0.052318185567855835,
        -0.015035799704492092,
        -0.025462502613663673,
        0.02562587894499302,
        -0.003998974338173866,
        0.009129341691732407,
        0.07043135166168213,
        -0.004517677705734968,
        -0.08051703125238419,
        0.0014796281466260552,
        0.05828672647476196,
        0.02732127346098423,
        -0.03499415144324303,
        -0.031034745275974274,
        -0.005702692084014416,
        -0.040223129093647,
        -0.004799958318471909,
        0.018715567886829376,
        0.04384651035070419,
        0.013568849302828312,
        -0.011443322524428368,
        0.005295567214488983,
        0.026522139087319374,
        0.002658095210790634,
        -0.03300406038761139,
        0.018211429938673973,
        -0.013894042000174522,
        0.013989650644361973,
        0.031047020107507706,
        -0.008311141282320023,
        0.01590598002076149,
        0.060290511697530746,
        0.01576240547001362,
        0.02187625877559185,
        0.043800316751003265,
        0.031320903450250626,
        -0.06651055067777634,
        -0.021002093330025673,
        0.0017026244895532727,
        0.043769653886556625,
        0.10567088425159454,
        0.05447397008538246,
        0.03038533218204975,
        -0.05251486599445343,
        0.006278094835579395,
        0.036366380751132965,
        -0.04047612473368645,
        0.028844239190220833,
        0.013570988550782204,
        0.09016293287277222,
        -0.004787171259522438,
        0.01950586773455143,
        -0.05719347298145294,
        0.061203483492136,
        0.01365590002387762,
        -0.014267620630562305,
        -0.024959318339824677,
        -0.017525024712085724,
        0.019045768305659294,
        0.015455638989806175,
        0.018744226545095444,
        -0.012427862733602524,
        0.02276451513171196,
        0.007119886577129364,
        0.026162952184677124,
        0.012351160869002342,
        -0.015322038903832436,
        0.030794212594628334,
        0.027505625039339066,
        -0.08122427016496658,
        -0.056815020740032196,
        0.028780920431017876,
        -0.05804600194096565,
        0.029232045635581017,
        0.09229617565870285,
        0.012091382406651974,
        -0.0043792868964374065,
        -0.059065081179142,
        -0.08049105107784271,
        0.010014526546001434,
        -0.00943391490727663,
        -0.021799413487315178,
        0.04687872156500816,
        -0.02472817152738571,
        -0.05067834630608559,
        -0.052253175526857376,
        0.008715991862118244,
        -0.016799505800008774,
        -0.04549355432391167,
        -0.042793650180101395,
        -0.011589781381189823,
        0.02598593384027481,
        0.02300962619483471,
        0.08437345176935196,
        -0.005691266618669033,
        -0.02574770711362362,
        0.03002670407295227,
        0.004122992046177387,
        -0.00882661622017622,
        0.01909799687564373,
        0.01614842191338539,
        0.03799080476164818,
        -0.04371938109397888,
        -0.007932179607450962,
        0.007009848486632109,
        0.016692185774445534,
        0.0018943115137517452,
        0.04915632680058479,
        0.0459667444229126,
        0.0007698669796809554,
        -0.0378001406788826,
        0.06169285625219345,
        0.006474153138697147,
        -0.02551594004034996,
        0.029698481783270836,
        0.017282065004110336,
        0.009382328949868679,
        0.01234542764723301,
        0.0458146370947361,
        -0.05962980166077614,
        0.053857170045375824,
        0.018979759886860847,
        -0.06830580532550812,
        0.047222405672073364,
        0.004947094712406397,
        0.006394018419086933,
        0.06749635934829712,
        -0.004976056516170502,
        -0.044039297848939896,
        0.005775265861302614,
        -0.021700462326407433,
        -0.04911866411566734,
        0.029284657910466194,
        0.0057007912546396255,
        -0.05791183561086655,
        -0.036271147429943085,
        0.027215855196118355,
        0.000328205554978922,
        0.011796397157013416,
        0.014365887269377708,
        -0.021071504801511765,
        -0.10476838052272797,
        0.03931521624326706,
        -0.01743827760219574,
        -0.06444519758224487,
        0.06594052165746689,
        -0.013583669438958168,
        0.023327721282839775,
        -0.040980175137519836,
        0.021110322326421738,
        -0.023542361333966255,
        0.009244954213500023,
        -0.027327876538038254,
        -0.0749981552362442,
        -0.05817040055990219,
        0.033675868064165115,
        -0.006241938564926386,
        0.015267791226506233,
        -0.005319511517882347,
        0.007725033443421125,
        -0.04769749939441681,
        -0.013632228597998619,
        -0.01671481318771839,
        0.032588712871074677,
        0.004994310438632965,
        0.009327513165771961,
        -0.014502864331007004,
        -0.021513426676392555,
        -0.041920777410268784,
        0.000736730988137424,
        -0.04845338687300682,
        0.05143485218286514,
        -0.00827883929014206,
        -0.05451349914073944,
        -0.018751125782728195,
        -0.028143448755145073,
        -0.027438942342996597,
        0.0018979490268975496,
        0.0029770773835480213,
        -0.052255671471357346,
        0.008816778659820557,
        -0.04883852228522301,
        -0.005153963807970285,
        0.03402094915509224,
        -0.033734340220689774,
        0.0250434298068285,
        -0.020967962220311165,
        -0.006132633425295353,
        -0.07388681918382645,
        -0.03740931302309036,
        0.025875000283122063,
        0.023692401126027107,
        0.00612619100138545,
        -0.022321289405226707,
        -0.035878535360097885,
        -0.028265153989195824,
        0.05367949604988098,
        0.011247171089053154,
        -0.020050087943673134,
        0.07264093309640884,
        0.06775902211666107,
        -0.00279391766525805,
        0.0012111783726140857,
        0.000033324729884043336,
        -0.008147984743118286,
        -0.023408658802509308,
        -0.0009141457267105579,
        -0.0390138104557991,
        -0.004014919511973858,
        -0.037028394639492035,
        0.027383441105484962,
        0.06490057706832886,
        -0.000045131921069696546,
        -0.039642851799726486,
        -0.028655976057052612,
        -0.01269892230629921,
        -0.020463932305574417,
        0.009898904711008072,
        -0.006316003855317831,
        -0.049614571034908295,
        -0.0066841524094343185,
        -0.026518603786826134,
        0.008593079634010792,
        -0.003961550071835518,
        0.03302085027098656,
        -0.022351538762450218,
        -0.036156121641397476,
        -0.044611334800720215,
        0.021284740418195724,
        -0.043991588056087494,
        0.003917429596185684,
        -0.03190663829445839,
        -0.0045702336356043816,
        -0.018654555082321167,
        0.011742550879716873,
        0.05492732673883438,
        -0.02513030730187893,
        -0.038381800055503845,
        0.00968407653272152,
        0.01182209700345993,
        0.04846900328993797,
        -0.028035493567585945,
        0.026404736563563347,
        0.041231412440538406,
        -0.026241928339004517,
        0.07928590476512909,
        0.061520665884017944,
        -0.021520253270864487,
        0.05087057501077652,
        0.06552571803331375,
        0.030050503090023994,
        -0.002204337390139699,
        -0.023577604442834854,
        -0.0306601133197546,
        -0.04351067543029785,
        -0.005328315310180187,
        -0.01005119550973177,
        -0.02883738838136196,
        -0.017970634624361992,
        -0.034061819314956665,
        -0.09152771532535553,
        -0.012920234352350235,
        -0.054658979177474976,
        0.006490966305136681,
        -0.005702045746147633,
        0.013751029968261719,
        -0.015532087534666061,
        -0.04882064089179039,
        -0.06106610968708992,
        -0.056693095713853836,
        0.01626153290271759,
        0.002411112654954195,
        0.04952302202582359,
        -0.056874003261327744,
        0.008347931317985058,
        -0.0002814563049469143,
        0.05288821458816528,
        0.03517848998308182,
        -0.04989904537796974,
        -0.04409780725836754,
        0.008727666921913624,
        -0.019816864281892776,
        -0.044541459530591965,
        0.050811536610126495,
        -0.016411324962973595,
        -0.01473113615065813,
        -0.0033838164526969194,
        -0.03577446565032005,
        -0.07643205672502518,
        0.01180155761539936,
        -0.0024393019266426563,
        -0.056923456490039825,
        0.024946225807070732,
        -0.03063299134373665,
        0.05805474892258644,
        -0.026666324585676193,
        0.03865901008248329,
        0.010353310965001583,
        0.03435457870364189,
        -0.03234299272298813,
        0.015178441070020199,
        0.008014033548533916,
        0.03488391637802124,
        -0.02252863347530365,
        0.0029658775310963392,
        -0.08343874663114548,
        -0.04188064485788345,
        0.006045202724635601,
        0.02174469269812107,
        -0.010302801616489887,
        0.00877392664551735,
        0.02698654495179653,
        0.011882752180099487,
        -0.03585568815469742,
        0.02313760109245777,
        0.03410400450229645,
        -0.02344358153641224,
        -0.06733264774084091,
        0.013219987042248249,
        -0.03404899314045906,
        -0.04966249316930771,
        -0.014130531810224056,
        -0.037043944001197815,
        0.030784595757722855,
        -0.051190052181482315,
        -0.01868394762277603,
        -0.017007501795887947,
        -0.0715363398194313,
        0.03724869713187218,
        -0.02842004969716072,
        0.040288373827934265,
        -0.007283140439540148,
        0.00501842750236392,
        -0.05653573200106621,
        0.012398875318467617,
        -0.00045440212124958634,
        -0.1044396162033081,
        -0.040580108761787415,
        0.019638027995824814,
        -0.038515642285346985,
        -0.07116620987653732,
        -0.0394931435585022,
        0.029516225680708885,
        0.0009498042636550963,
        0.04369128495454788,
        0.003504744963720441,
        0.02860836312174797,
        -0.015155916102230549,
        -0.021670715883374214,
        0.0023334589786827564,
        0.044438689947128296,
        0.023793401196599007,
        0.039728522300720215,
        0.07858478277921677,
        0.01348444726318121,
        0.030168594792485237,
        -0.01906987838447094,
        0.04200403019785881,
        -0.007454268634319305,
        0.017389994114637375,
        -0.018342411145567894,
        -0.006242978852242231,
        0.0008583567687310278,
    ]

    return [
        TextNode(
            text="lorem ipsum",
            id_="c330d77f-90bd-4c51-9ed2-57d8d693b3b0",
            relationships={NodeRelationship.SOURCE: RelatedNodeInfo(node_id="test-0")},
            metadata={
                "author": "Stephen King",
                "theme": "Friendship",
            },
            embedding=embedding,
        ),
        TextNode(
            text="lorem ipsum",
            id_="c3d1e1dd-8fb4-4b8f-b7ea-7fa96038d39d",
            relationships={NodeRelationship.SOURCE: RelatedNodeInfo(node_id="test-1")},
            metadata={
                "director": "Francis Ford Coppola",
                "theme": "Mafia",
            },
            embedding=embedding,
        ),
        TextNode(
            text="lorem ipsum",
            id_="c3ew11cd-8fb4-4b8f-b7ea-7fa96038d39f",
            relationships={NodeRelationship.SOURCE: RelatedNodeInfo(node_id="test-2")},
            metadata={
                "director": "Christopher Nolan",
            },
            embedding=embedding,
        ),
        TextNode(
            text="I was taught that the way of progress was neither swift nor easy.",
            id_="0b31ae71-b797-4e88-8495-031371a7752e",
            relationships={NodeRelationship.SOURCE: RelatedNodeInfo(node_id="text-3")},
            metadata={
                "author": "Marie Curie",
            },
            embedding=embedding,
        ),
        TextNode(
            text=(
                "The important thing is not to stop questioning."
                + " Curiosity has its own reason for existing."
            ),
            id_="bd2e080b-159a-4030-acc3-d98afd2ba49b",
            relationships={NodeRelationship.SOURCE: RelatedNodeInfo(node_id="text-4")},
            metadata={
                "author": "Albert Einstein",
            },
            embedding=embedding,
        ),
        TextNode(
            text=(
                "I am no bird; and no net ensnares me;"
                + " I am a free human being with an independent will."
            ),
            id_="f658de3b-8cef-4d1c-8bed-9a263c907251",
            relationships={NodeRelationship.SOURCE: RelatedNodeInfo(node_id="text-5")},
            metadata={
                "author": "Charlotte Bronte",
            },
            embedding=embedding,
        ),
    ]


@pytest.fixture(scope="session")
def wiremock_server() -> Generator[WireMockContainer, None, None]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with wiremock_container(image="wiremock/wiremock:3.9.1-1", secure=False) as wm:
        Config.base_url = wm.get_url("__admin")

        with open(os.path.join(current_dir, "__files/account/me/response_1.json")) as f:
            Mappings.create_mapping(
                Mapping(
                    request=MappingRequest(
                        method=HttpMethods.GET,
                        url="/accounts/me",
                        headers={
                            "Accept": {
                                "equalTo": "application/vnd.wordlift.account-info.v2+json"
                            },
                            "Authorization": {"equalTo": "Key " + KEY},
                        },
                    ),
                    response=MappingResponse(status=200, body=f.read()),
                    persistent=False,
                )
            )

        Mappings.create_mapping(
            Mapping(
                request=MappingRequest(
                    method=HttpMethods.PUT,
                    url="/vector-search/nodes-collection",
                    headers={
                        "Authorization": {"equalTo": "Key " + KEY},
                        "Content-Type": {"equalTo": "application/json"},
                    },
                ),
                response=MappingResponse(status=200),
                persistent=False,
            )
        )

        Mappings.create_mapping(
            Mapping(
                request=MappingRequest(
                    method=HttpMethods.DELETE,
                    url_path="/entities",
                    headers={
                        "Authorization": {"equalTo": "Key " + KEY},
                    },
                    query_parameters={
                        "id": {
                            "hasExactly": [
                                {
                                    "equalTo": "https://data.example.org/dataset/c330d77f-90bd-4c51-9ed2-57d8d693b3b0"
                                },
                                {
                                    "equalTo": "https://data.example.org/dataset/c3d1e1dd-8fb4-4b8f-b7ea-7fa96038d39d"
                                },
                                {
                                    "equalTo": "https://data.example.org/dataset/c3ew11cd-8fb4-4b8f-b7ea-7fa96038d39f"
                                },
                                {
                                    "equalTo": "https://data.example.org/dataset/0b31ae71-b797-4e88-8495-031371a7752e"
                                },
                                {
                                    "equalTo": "https://data.example.org/dataset/bd2e080b-159a-4030-acc3-d98afd2ba49b"
                                },
                                {
                                    "equalTo": "https://data.example.org/dataset/f658de3b-8cef-4d1c-8bed-9a263c907251"
                                },
                            ]
                        }
                    },
                ),
                response=MappingResponse(status=200),
                persistent=False,
            )
        )

        with open(
            os.path.join(current_dir, "__files/vector-search/queries/response_1.json")
        ) as f:
            Mappings.create_mapping(
                Mapping(
                    request=MappingRequest(
                        method=HttpMethods.POST,
                        url="/vector-search/queries",
                        headers={
                            "Authorization": {"equalTo": "Key " + KEY},
                            "Accept": {"equalTo": "application/json"},
                            "Content-Type": {"equalTo": "application/json"},
                        },
                    ),
                    response=MappingResponse(status=200, body=f.read()),
                    persistent=False,
                )
            )

        yield wm


@pytest.fixture(scope="session")
def configuration(wiremock_server) -> Configuration:
    configuration = Configuration(
        host=wiremock_server.get_url(""),
    )

    configuration.api_key["ApiKey"] = KEY
    configuration.api_key_prefix["ApiKey"] = "Key"

    return configuration


@pytest.fixture(scope="session")
def vector_store(configuration: Configuration) -> WordliftVectorStore:
    return WordliftVectorStore(configuration=configuration)


@pytest.mark.asyncio()
@pytest.mark.parametrize("use_async", [True, False])
async def test_add(
    vector_store: WordliftVectorStore, node_embeddings: List[TextNode], use_async: bool
) -> None:
    if use_async:
        await vector_store.async_add(node_embeddings)
    else:
        vector_store.add(node_embeddings)


@pytest.mark.asyncio()
@pytest.mark.parametrize("use_async", [True, False])
async def test_delete_nodes(
    vector_store: WordliftVectorStore, node_embeddings: List[TextNode], use_async: bool
) -> None:
    vector_store.add(node_embeddings)
    if use_async:
        await vector_store.adelete_nodes(
            node_ids=[
                "c330d77f-90bd-4c51-9ed2-57d8d693b3b0",
                "c3d1e1dd-8fb4-4b8f-b7ea-7fa96038d39d",
                "c3ew11cd-8fb4-4b8f-b7ea-7fa96038d39f",
                "0b31ae71-b797-4e88-8495-031371a7752e",
                "bd2e080b-159a-4030-acc3-d98afd2ba49b",
                "f658de3b-8cef-4d1c-8bed-9a263c907251",
            ]
        )
    else:
        vector_store.delete_nodes(
            node_ids=[
                "c330d77f-90bd-4c51-9ed2-57d8d693b3b0",
                "c3d1e1dd-8fb4-4b8f-b7ea-7fa96038d39d",
                "c3ew11cd-8fb4-4b8f-b7ea-7fa96038d39f",
                "0b31ae71-b797-4e88-8495-031371a7752e",
                "bd2e080b-159a-4030-acc3-d98afd2ba49b",
                "f658de3b-8cef-4d1c-8bed-9a263c907251",
            ]
        )


@pytest.mark.asyncio()
@pytest.mark.parametrize("use_async", [True, False])
async def test_add_to_wordlift_and_query(
    vector_store: WordliftVectorStore,
    node_embeddings: List[TextNode],
    use_async: bool,
) -> None:
    if use_async:
        await vector_store.async_add(node_embeddings)
        res = await vector_store.aquery(
            VectorStoreQuery(
                query_embedding=node_embeddings[0].embedding, similarity_top_k=1
            )
        )
    else:
        vector_store.add(node_embeddings)
        res = vector_store.query(
            VectorStoreQuery(
                query_embedding=node_embeddings[0].embedding, similarity_top_k=1
            )
        )

    assert res.nodes
    assert res.nodes[0].get_content() == "lorem ipsum"
