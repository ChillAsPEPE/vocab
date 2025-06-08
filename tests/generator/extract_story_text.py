import json
import re

# --- Story Data (Paste your JSON string here) ---
# This should be a string representation of a JSON array of chapter objects.
ALL_STORIES_JSON_STRING = """
[
  {
    "chapter_title": "Shadows in the Neon City",
    "chapter_num": 0,
    "story_sentences": [
      {
        "english": "Detective Lena walked <word id='_abreast' class='word-eng-link'>abreast</word> with her partner, Kai, through the neon-lit streets of the city.",
        "korean": "형사 레나는 파트너 카이와 함께 네온 불빛이 비추는 도시 거리를 <word id='_abreast' class='word-target-kr'>나란히</word> 걸었다."
      },
      {
        "english": "Kai's <word id='_affectation' class='word-eng-link'>affectation</word> of confidence hid his nervousness about their new case.",
        "korean": "카이의 자신감이라는 <word id='_affectation' class='word-target-kr'>가식</word>은 새 사건에 대한 그의 초조함을 숨겼다."
      },
      {
        "english": "They needed to <word id='_ally' class='word-eng-link'>ally</word> with the underground informants to uncover the truth.",
        "korean": "그들은 진실을 밝히기 위해 지하 정보원들과 <word id='_ally' class='word-target-kr'>동맹을 맺다</word> 필요했다."
      },
      {
        "english": "An <word id='_anonymous' class='word-eng-link'>anonymous</word> tip had led them to a hidden warehouse in the city's underbelly.",
        "korean": "<word id='_anonymous' class='word-target-kr'>익명의</word> 제보가 그들을 도시의 어두운 구석에 숨겨진 창고로 이끌었다."
      },
      {
        "english": "Lena tried to <word id='_anticipate' class='word-eng-link'>anticipate</word> the dangers that might await them inside.",
        "korean": "레나는 안에서 그들을 기다릴지도 모르는 위험을 <word id='_anticipate' class='word-target-kr'>예상하다</word> 애썼다."
      },
      {
        "english": "The warehouse was filled with <word id='_archaic' class='word-eng-link'>archaic</word> machines, relics of a forgotten era.",
        "korean": "창고는 잊혀진 시대의 유물인 <word id='_archaic' class='word-target-kr'>고대의</word> 기계들로 가득했다."
      },
      {
        "english": "From one <word id='_aspect' class='word-eng-link'>aspect</word>, the machines seemed harmless, but Lena sensed a hidden threat.",
        "korean": "한 <word id='_aspect' class='word-target-kr'>측면, 양상</word>에서 그 기계들은 무해해 보였지만, 레나는 숨겨진 위협을 감지했다."
      },
      {
        "english": "Kai's reckless <word id='_behavior' class='word-eng-link'>behavior</word> nearly triggered an alarm as he explored the area.",
        "korean": "카이의 무모한 <word id='_behavior' class='word-target-kr'>행동</word>은 그가 그 지역을 탐색할 때 거의 경보를 울릴 뻔했다."
      },
      {
        "english": "The <word id='_ceaseless' class='word-eng-link'>ceaseless</word> hum of the machines filled the air, creating an eerie atmosphere.",
        "korean": "기계들의 <word id='_ceaseless' class='word-target-kr'>끊임없는</word> 웅웅거리는 소리가 공기를 채우며 으스스한 분위기를 만들었다."
      },
      {
        "english": "Lena knew they had to <word id='_change' class='word-eng-link'>change</word> their approach to avoid detection.",
        "korean": "레나는 그들이 발각되지 않도록 접근 방식을 <word id='_change' class='word-target-kr'>변화시키다</word> 해야 한다는 것을 알았다."
      }
    ]
  },
  {
    "chapter_title": "The Hidden Confederacy",
    "chapter_num": 1,
    "story_sentences": [
      {
        "english": "Inside the warehouse, they discovered evidence of a secret <word id='_confederacy' class='word-eng-link'>confederacy</word> plotting against the city.",
        "korean": "창고 안에서 그들은 도시를 상대로 음모를 꾸미는 비밀 <word id='_confederacy' class='word-target-kr'>연합, 동맹</word>의 증거를 발견했다."
      },
      {
        "english": "Lena used a laser to <word id='_cut' class='word-eng-link'>cut</word> through a locked door, revealing a hidden chamber.",
        "korean": "레나는 레이저를 사용해 잠긴 문을 <word id='_cut' class='word-target-kr'>나누다</word> 하고, 숨겨진 방을 드러냈다."
      },
      {
        "english": "The chamber was in a state of <word id='_disturbance' class='word-eng-link'>disturbance</word>, with papers scattered everywhere.",
        "korean": "그 방은 서류가 사방에 흩어져 있어 <word id='_disturbance' class='word-target-kr'>혼란</word> 상태에 있었다."
      },
      {
        "english": "A document helped <word id='_elucidate' class='word-eng-link'>elucidate</word> the confederacy's plans, detailing a sabotage operation.",
        "korean": "한 문서가 연합의 계획을 <word id='_elucidate' class='word-target-kr'>명료하게 하다</word> 도왔으며, 사보타주 작전을 상세히 설명했다."
      },
      {
        "english": "Kai, ever <word id='_enterprising' class='word-eng-link'>enterprising</word>, suggested hacking into the confederacy's network.",
        "korean": "늘 <word id='_enterprising' class='word-target-kr'>진취적인</word> 카이는 연합의 네트워크를 해킹할 것을 제안했다."
      },
      {
        "english": "They found a message that tried to <word id='_entice' class='word-eng-link'>entice</word> new recruits with promises of power.",
        "korean": "그들은 새로운 모집자들을 권력의 약속으로 <word id='_entice' class='word-target-kr'>유혹하다</word> 시도하는 메시지를 발견했다."
      },
      {
        "english": "The message was <word id='_equivocal' class='word-eng-link'>equivocal</word>, leaving Lena unsure of the sender's true intentions.",
        "korean": "그 메시지는 <word id='_equivocal' class='word-target-kr'>애매한</word> 내용이어서 레나는 발신자의 진짜 의도를 확신할 수 없었다."
      },
      {
        "english": "Lena feared the confederacy aimed to <word id='_exterminate' class='word-eng-link'>exterminate</word> the city's power grid.",
        "korean": "레나는 연합이 도시의 전력망을 <word id='_exterminate' class='word-target-kr'>멸종시키다</word> 목표로 하고 있다고 두려워했다."
      },
      {
        "english": "They needed to <word id='_fortify' class='word-eng-link'>fortify</word> their defenses before confronting the enemy.",
        "korean": "그들은 적과 대면하기 전에 방어를 <word id='_fortify' class='word-target-kr'>강화하다</word> 필요했다."
      },
      {
        "english": "The <word id='_frightful' class='word-eng-link'>frightful</word> reality of the threat began to sink in as they left the chamber.",
        "korean": "그들이 방을 떠나면서 위협의 <word id='_frightful' class='word-target-kr'>무시무시한</word> 현실이 서서히 다가왔다."
      }
    ]
  },
  {
    "chapter_title": "A Dangerous Pursuit",
    "chapter_num": 2,
    "story_sentences": [
      {
        "english": "Lena's <word id='_immunity' class='word-eng-link'>immunity</word> to fear kept her focused as they pursued the confederacy's leader.",
        "korean": "레나의 두려움에 대한 <word id='_immunity' class='word-target-kr'>면제</word>는 그들이 연합의 지도자를 추적할 때 그녀를 집중하게 했다."
      },
      {
        "english": "Kai worked to <word id='_improve' class='word-eng-link'>improve</word> their tracking device to locate the leader's hideout.",
        "korean": "카이는 지도자의 은신처를 찾기 위해 추적 장치를 <word id='_improve' class='word-target-kr'>개선하다</word> 노력했다."
      },
      {
        "english": "They couldn't afford to <word id='_lose_sight_of' class='word-eng-link'>lose sight of</word> their mission amidst the chaos.",
        "korean": "그들은 혼란 속에서 임무를 <word id='_lose_sight_of' class='word-target-kr'>잊다</word> 여유가 없었다."
      },
      {
        "english": "The leader operated from a <word id='_mammoth' class='word-eng-link'>mammoth</word> skyscraper in the city's core.",
        "korean": "지도자는 도시 중심에 있는 <word id='_mammoth' class='word-target-kr'>거대한</word> 마천루에서 활동했다."
      },
      {
        "english": "Lena studied the <word id='_nuts_and_bolts' class='word-eng-link'>nuts and bolts</word> of the skyscraper's security system.",
        "korean": "레나는 마천루의 보안 시스템의 <word id='_nuts_and_bolts' class='word-target-kr'>~의 기본</word>을 연구했다."
      },
      {
        "english": "They needed a plan to <word id='_permit' class='word-eng-link'>permit</word> them to bypass the guards undetected.",
        "korean": "그들은 경비를 들키지 않고 우회할 수 있도록 <word id='_permit' class='word-target-kr'>허락하다</word> 계획이 필요했다."
      },
      {
        "english": "The leader's <word id='_radical' class='word-eng-link'>radical</word> ideology was the root of the confederacy's actions.",
        "korean": "지도자의 <word id='_radical' class='word-target-kr'>근본적인</word> 이념은 연합의 행동의 뿌리였다."
      },
      {
        "english": "His <word id='_radical' class='word-eng-link'>radical</word> plans threatened to reshape the city's future.",
        "korean": "그의 <word id='_radical' class='word-target-kr'>급진적인</word> 계획은 도시의 미래를 재편할 위협이 되었다."
      },
      {
        "english": "Lena found a <word id='_reference' class='word-eng-link'>reference</word> to a secret meeting in the skyscraper's archives.",
        "korean": "레나는 마천루의 기록 보관소에서 비밀 회의에 대한 <word id='_reference' class='word-target-kr'>언급</word>을 발견했다."
      },
      {
        "english": "They had to <word id='_separate' class='word-eng-link'>separate</word> to cover more ground and find the meeting room.",
        "korean": "그들은 더 많은 영역을 커버하고 회의실을 찾기 위해 <word id='_separate' class='word-target-kr'>분리하다</word> 해야 했다."
      }
    ]
  },
  {
    "chapter_title": "The Sparse Trail",
    "chapter_num": 3,
    "story_sentences": [
      {
        "english": "Clues in the skyscraper were <word id='_sparse' class='word-eng-link'>sparse</word>, making the search frustrating.",
        "korean": "마천루의 단서는 <word id='_sparse' class='word-target-kr'>희박한</word> 상태여서 수색이 좌절스러웠다."
      },
      {
        "english": "Lena felt a <word id='_sting' class='word-eng-link'>sting</word> of doubt as they navigated the dark corridors.",
        "korean": "레나는 어두운 복도를 헤쳐나가며 의심의 <word id='_sting' class='word-target-kr'>따끔따끔하게 하다</word> 느낌을 받았다."
      },
      {
        "english": "Kai's decision to <word id='_support' class='word-eng-link'>support</word> Lena's plan gave her renewed confidence.",
        "korean": "카이의 레나의 계획을 <word id='_support' class='word-target-kr'>지지하다</word> 결정은 그녀에게 새로운 자신감을 주었다."
      },
      {
        "english": "They found a <word id='_tangible' class='word-eng-link'>tangible</word> lead: a keycard hidden in a vent.",
        "korean": "그들은 <word id='_tangible' class='word-target-kr'>실재적인</word> 단서를 찾았다: 통풍구에 숨겨진 키카드였다."
      },
      {
        "english": "Lena had to <word id='_tolerate' class='word-eng-link'>tolerate</word> the tension as they approached the meeting room.",
        "korean": "레나는 회의실에 접근하면서 긴장을 <word id='_tolerate' class='word-target-kr'>참다</word> 해야 했다."
      },
      {
        "english": "She <word id='_train' class='word-eng-link'>train</word> her flashlight on a locked door, revealing a keypad.",
        "korean": "그녀는 손전등을 잠긴 문에 <word id='_train' class='word-target-kr'>~로 향하게 하다</word> 비추며 키패드를 드러냈다."
      },
      {
        "english": "The keypad's instructions were <word id='_unambiguous' class='word-eng-link'>unambiguous</word>, requiring a specific code.",
        "korean": "키패드의 지침은 <word id='_unambiguous' class='word-target-kr'>명확한</word> 것으로, 특정 코드를 요구했다."
      },
      {
        "english": "They were <word id='_virtually' class='word-eng-link'>virtually</word> at the heart of the confederacy's operations.",
        "korean": "그들은 <word id='_virtually' class='word-target-kr'>사실상</word> 연합의 작전 중심에 있었다."
      },
      {
        "english": "The room was <word id='_virtually' class='word-eng-link'>virtually</word> empty, except for a single data drive.",
        "korean": "그 방은 단일 데이터 드라이브를 제외하고 <word id='_virtually' class='word-target-kr'>거의</word> 비어 있었다."
      },
      {
        "english": "Lena remained <word id='_wary' class='word-eng-link'>wary</word> of traps as she retrieved the drive.",
        "korean": "레나는 드라이브를 회수하면서 함정에 대해 <word id='_wary' class='word-target-kr'>주의 깊은</word> 태도를 유지했다."
      }
    ]
  },
  {
    "chapter_title": "Echoes of Wealth",
    "chapter_num": 4,
    "story_sentences": [
      {
        "english": "The data drive revealed the confederacy's <word id='_wealth' class='word-eng-link'>wealth</word>, amassed through illegal means.",
        "korean": "데이터 드라이브는 연합의 불법적인 수단으로 축적된 <word id='_wealth' class='word-target-kr'>풍부함</word>을 드러냈다."
      },
      {
        "english": "Lena's <word id='_agile' class='word-eng-link'>agile</word> mind quickly pieced together the financial trail.",
        "korean": "레나의 <word id='_agile' class='word-target-kr'>민첩한</word> 두뇌는 재정적 흔적을 빠르게 맞췄다."
      },
      {
        "english": "They escaped through an <word id='_ample' class='word-eng-link'>ample</word> ventilation shaft to avoid detection.",
        "korean": "그들은 발각을 피하기 위해 <word id='_ample' class='word-target-kr'>넓은</word> 환풍구를 통해 탈출했다."
      },
      {
        "english": "The leader had <word id='_arbitrarily' class='word-eng-link'>arbitrarily</word> chosen targets to destabilize the city.",
        "korean": "지도자는 도시를 불안정하게 만들기 위해 <word id='_arbitrarily' class='word-target-kr'>임의로</word> 표적을 선택했다."
      },
      {
        "english": "Lena decided to <word id='_break_with' class='word-eng-link'>break with</word> protocol and contact an old ally.",
        "korean": "레나는 규정을 <word id='_break_with' class='word-target-kr'>관계를 끊다</word> 하고 옛 동맹에게 연락하기로 결정했다."
      },
      {
        "english": "She chose to <word id='_break_with' class='word-eng-link'>break with</word> her cautious approach for a bolder move.",
        "korean": "그녀는 신중한 접근 방식을 <word id='_break_with' class='word-target-kr'>그만두다</word> 하고 더 대담한 행동을 선택했다."
      },
      {
        "english": "The ally's hideout was bathed in the <word id='_brightness' class='word-eng-link'>brightness</word> of holographic displays.",
        "korean": "동맹의 은신처는 홀로그램 디스플레이의 <word id='_brightness' class='word-target-kr'>빛</word>으로 가득했다."
      },
      {
        "english": "Memories of past cases began to <word id='_conjure' class='word-eng-link'>conjure</word> in Lena's mind as they talked.",
        "korean": "과거 사건의 기억이 그들이 대화하면서 레나의 마음에 <word id='_conjure' class='word-target-kr'>불러내다, 상기시키다</word> 시작했다."
      },
      {
        "english": "The ally <word id='_conjure' class='word-eng-link'>conjure</word> a plan to infiltrate the confederacy's next meeting.",
        "korean": "동맹은 연합의 다음 회의에 잠입할 계획을 <word id='_conjure' class='word-target-kr'>간청하다</word> 제시했다."
      },
      {
        "english": "Their goals were in <word id='_correspondent' class='word-eng-link'>correspondent</word> with each other, ensuring cooperation.",
        "korean": "그들의 목표는 서로 <word id='_correspondent' class='word-target-kr'>일치</word>하여 협력을 보장했다."
      }
    ]
  },
  {
    "chapter_title": "Letters of Deception",
    "chapter_num": 5,
    "story_sentences": [
      {
        "english": "The ally revealed a history of <word id='_correspondent' class='word-eng-link'>correspondent</word> with the confederacy, exchanging coded letters.",
        "korean": "동맹은 연합과의 암호화된 편지를 주고받은 <word id='_correspondent' class='word-target-kr'>서신 왕래 (통신)</word>의 역사를 밝혔다."
      },
      {
        "english": "Their alliance was <word id='_durable' class='word-eng-link'>durable</word>, surviving years of covert operations.",
        "korean": "그들의 동맹은 수년간의 비밀 작전을 견딘 <word id='_durable' class='word-target-kr'>지속되는</word> 것이었다."
      },
      {
        "english": "A <word id='_dwarf' class='word-eng-link'>dwarf</word> robot assisted them, decoding the letters with precision.",
        "korean": "<word id='_dwarf' class='word-target-kr'>난쟁이</word> 로봇이 그들을 도와 편지를 정밀하게 해독했다."
      },
      {
        "english": "The confederacy's plans were not <word id='_extinct' class='word-eng-link'>extinct</word> but evolving rapidly.",
        "korean": "연합의 계획은 <word id='_extinct' class='word-target-kr'>멸종된</word> 것이 아니라 빠르게 진화하고 있었다."
      },
      {
        "english": "Lena suspected someone had <word id='_fabricate' class='word-eng-link'>fabricate</word> false leads to mislead them.",
        "korean": "레나는 누군가가 그들을 오도하기 위해 거짓 단서를 <word id='_fabricate' class='word-target-kr'>만들어내다</word> 의심했다."
      },
      {
        "english": "A <word id='_flake' class='word-eng-link'>flake</word> of paint on the robot revealed it was stolen from a rival group.",
        "korean": "로봇에 묻은 페인트 <word id='_flake' class='word-target-kr'>파편</word>은 그것이 경쟁 단체에서 도난당한 것임을 드러냈다."
      },
      {
        "english": "Lena harbored no <word id='_grudge' class='word-eng-link'>grudge</word> against the ally, despite the deception.",
        "korean": "레나는 속임수에도 불구하고 동맹에 대해 어떤 <word id='_grudge' class='word-target-kr'>원한</word>도 품지 않았다."
      },
      {
        "english": "The deception caused no <word id='_harm' class='word-eng-link'>harm</word>, as the decoded letters were genuine.",
        "korean": "그 속임수는 해독된 편지가 진짜였기 때문에 아무런 <word id='_harm' class='word-target-kr'>손해</word>를 끼치지 않았다."
      },
      {
        "english": "The ally was <word id='_innocent' class='word-eng-link'>innocent</word> of any betrayal, acting in the city's interest.",
        "korean": "동맹은 도시의 이익을 위해 행동하며 어떤 배신에도 <word id='_innocent' class='word-target-kr'>결백한</word> 상태였다."
      },
      {
        "english": "<word id='_in_the_course' class='word-eng-link'>In the course</word> of their work, they uncovered the meeting's location.",
        "korean": "그들의 작업 <word id='_in_the_course' class='word-target-kr'>~동안에</word> 그들은 회의 장소를 알아냈다."
      }
    ]
  },
  {
    "chapter_title": "Departure to the Abyss",
    "chapter_num": 6,
    "story_sentences": [
      {
        "english": "Lena and Kai prepared to <word id='_leave' class='word-eng-link'>leave</word> for the meeting site, a derelict factory.",
        "korean": "레나와 카이는 버려진 공장인 회의 장소로 <word id='_leave' class='word-target-kr'>떠나다</word> 준비했다."
      },
      {
        "english": "They <word id='_liken' class='word-eng-link'>liken</word> the factory to a fortress, impenetrable and foreboding.",
        "korean": "그들은 공장을 난공불락의 요새에 <word id='_liken' class='word-target-kr'>비유하다</word> 보았다."
      },
      {
        "english": "The plan was <word id='_literally' class='word-eng-link'>literally</word> their only chance to stop the confederacy.",
        "korean": "그 계획은 <word id='_literally' class='word-target-kr'>실제로</word> 연합을 막을 유일한 기회였다."
      },
      {
        "english": "Their approach was <word id='_moderate' class='word-eng-link'>moderate</word>, avoiding unnecessary risks.",
        "korean": "그들의 접근 방식은 불필요한 위험을 피하는 <word id='_moderate' class='word-target-kr'>온건한</word> 것이었다."
      },
      {
        "english": "They aimed to <word id='_prolong' class='word-eng-link'>prolong</word> their stealth to gather more evidence.",
        "korean": "그들은 더 많은 증거를 수집하기 위해 은밀함을 <word id='_prolong' class='word-target-kr'>연장하다</word> 목표로 했다."
      },
      {
        "english": "Lena worked to <word id='_purify' class='word-eng-link'>purify</word> their strategy, eliminating flaws.",
        "korean": "레나는 전략의 결함을 제거하며 <word id='_purify' class='word-target-kr'>정화하다</word> 노력했다."
      },
      {
        "english": "Their <word id='_reasonable' class='word-eng-link'>reasonable</word> plan relied on precise timing.",
        "korean": "그들의 <word id='_reasonable' class='word-target-kr'>이치에 맞는</word> 계획은 정확한 타이밍에 의존했다."
      },
      {
        "english": "The factory's air was <word id='_refined' class='word-eng-link'>refined</word>, filtered to keep out toxins.",
        "korean": "공장의 공기는 독소를 걸러내기 위해 <word id='_refined' class='word-target-kr'>정제된</word> 상태였다."
      },
      {
        "english": "Kai had to <word id='_reprove' class='word-eng-link'>reprove</word> himself for a momentary lapse in focus.",
        "korean": "카이는 순간적인 집중력 저하를 스스로 <word id='_reprove' class='word-target-kr'>꾸짖다</word> 해야 했다."
      },
      {
        "english": "Lena's <word id='_resilient' class='word-eng-link'>resilient</word> spirit kept them moving forward.",
        "korean": "레나의 <word id='_resilient' class='word-target-kr'>탄력 있는</word> 정신은 그들을 계속 앞으로 나아가게 했다."
      }
    ]
  },
  {
    "chapter_title": "The Final Scope",
    "chapter_num": 7,
    "story_sentences": [
      {
        "english": "They needed to <word id='_retain' class='word-eng-link'>retain</word> their cover to infiltrate the meeting.",
        "korean": "그들은 회의에 잠입하기 위해 은폐를 <word id='_retain' class='word-target-kr'>유지하다</word> 필요했다."
      },
      {
        "english": "Resources were <word id='_scarce' class='word-eng-link'>scarce</word>, forcing them to rely on ingenuity.",
        "korean": "자원이 <word id='_scarce' class='word-target-kr'>부족한</word> 상태여서 그들은 창의력에 의존해야 했다."
      },
      {
        "english": "The <word id='_scope' class='word-eng-link'>scope</word> of the confederacy's plan was staggering, targeting the entire city.",
        "korean": "연합의 계획의 <word id='_scope' class='word-target-kr'>범위</word>는 도시 전체를 겨냥한 놀라운 것이었다."
      },
      {
        "english": "The factory's <word id='_shabby' class='word-eng-link'>shabby</word> exterior hid a high-tech interior.",
        "korean": "공장의 <word id='_shabby' class='word-target-kr'>초라한</word> 외관은 첨단 내부를 숨겼다."
      },
      {
        "english": "Their advantage was <word id='_short-lived' class='word-eng-link'>short-lived</word> as alarms began to sound.",
        "korean": "그들의 이점은 경보가 울리기 시작하면서 <word id='_short-lived' class='word-target-kr'>단기간의</word> 것이었다."
      },
      {
        "english": "Lena worked to <word id='_solidify' class='word-eng-link'>solidify</word> their escape plan under pressure.",
        "korean": "레나는 압박 속에서 탈출 계획을 <word id='_solidify' class='word-target-kr'>결속시키다</word> 노력했다."
      },
      {
        "english": "The leader's <word id='_substantial' class='word-eng-link'>substantial</word> defenses made escape difficult.",
        "korean": "지도자의 <word id='_substantial' class='word-target-kr'>튼튼한</word> 방어는 탈출을 어렵게 했다."
      },
      {
        "english": "They made a <word id='_substantial' class='word-eng-link'>substantial</word> breakthrough, capturing key evidence.",
        "korean": "그들은 핵심 증거를 확보하며 <word id='_substantial' class='word-target-kr'>상당한</word> 돌파구를 만들었다."
      },
      {
        "english": "They found a <word id='_vacant' class='word-eng-link'>vacant</word> service tunnel to exit the factory.",
        "korean": "그들은 공장에서 나가기 위해 <word id='_vacant' class='word-target-kr'>텅 빈</word> 서비스 터널을 찾았다."
      },
      {
        "english": "The leader, a true <word id='_villain' class='word-eng-link'>villain</word>, had escaped, but not for long.",
        "korean": "지도자는 진정한 <word id='_villain' class='word-target-kr'>악당</word>이었지만, 오래 도망치지 못했다."
      }
    ]
  },
  {
    "chapter_title": "The Wary Escape",
    "chapter_num": 8,
    "story_sentences": [
      {
        "english": "Lena remained <word id='_wary_of' class='word-eng-link'>wary of</word> pursuers as they fled through the tunnel.",
        "korean": "레나는 터널을 통해 도망치며 추격자들을 <word id='_wary_of' class='word-target-kr'>조심(경계)하는</word> 태도를 유지했다."
      },
      {
        "english": "The tunnel's walls were <word id='_shriveled' class='word-eng-link'>shriveled</word>, crumbling under their touch.",
        "korean": "터널의 벽은 그들의 손길 아래 <word id='_shriveled' class='word-target-kr'>시든</word> 상태로 부서졌다."
      }
    ]
  }
]
"""

# --- Function to strip HTML-like tags from a string ---
def strip_tags(html_text):
    """단순히 <...> 태그를 제거합니다."""
    return re.sub(r'<[^>]+>', '', html_text)

# --- Main script logic for text extraction ---
def extract_english_text(json_string):
    """
    주어진 JSON 문자열에서 챕터 제목과 영어 문장을 추출하여 인쇄합니다.
    <word> 태그는 제거됩니다.
    """
    extracted_lines = []
    try:
        # 비표준 공백(예: U+00A0) 정리
        cleaned_json_string = json_string.replace("\u00a0", " ")
        stories = json.loads(cleaned_json_string)

        if not isinstance(stories, list):
            extracted_lines.append("오류: 입력된 JSON이 챕터 목록이 아닙니다.")
            return "\n".join(extracted_lines)

        for chapter in stories:
            if not isinstance(chapter, dict):
                extracted_lines.append(f"경고: 잘못된 챕터 항목 건너뛰기: {chapter}")
                continue

            chapter_num = chapter.get("chapter_num", "N/A")
            chapter_title = chapter.get("chapter_title", "제목 없음")
            extracted_lines.append(f"Chapter {chapter_num}. {chapter_title}\n")

            story_sentences = chapter.get("story_sentences")
            if isinstance(story_sentences, list):
                for sentence_pair in story_sentences:
                    if isinstance(sentence_pair, dict) and "english" in sentence_pair:
                        english_sentence_raw = sentence_pair["english"]
                        # <word> 태그 제거
                        plain_english_sentence = strip_tags(english_sentence_raw)
                        extracted_lines.append(plain_english_sentence)
                    else:
                        extracted_lines.append(f"  경고: 잘못된 문장 쌍 건너뛰기: {sentence_pair}")
                extracted_lines.append("") # 챕터 사이에 빈 줄 추가
            else:
                extracted_lines.append(f"  경고: '{chapter_title}' 챕터에 'story_sentences' 목록이 없습니다.\n")
                
    except json.JSONDecodeError as e:
        extracted_lines.append(f"JSON 디코딩 오류: {e}")
        extracted_lines.append(f"문제의 JSON 문자열 (처음 200자): {json_string[:200]}...")
    except Exception as e:
        extracted_lines.append(f"처리 중 예외 발생: {e}")
        
    return "\n".join(extracted_lines)

# 스크립트 실행 및 결과 인쇄
if __name__ == '__main__':
    extracted_text_output = extract_english_text(ALL_STORIES_JSON_STRING)
    print(extracted_text_output)
