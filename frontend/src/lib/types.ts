export type Bot = {
  id: string;
  name: string;
  description: string | null;
  patient_impact_level: 1 | 2 | 3;
  patient_impact_score: number;
  pis_reasoning: string | null;
  automation_debt_score: number;
  last_tested_at: string | null;
  last_test_result: "pass" | "fail" | null;
  registered_at: string;
};




export type Fleet = {
  hospital: string;
  bot_count: number;
  bots: Bot[];
};