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



export type BlastNode = {
  id: string;
  name: string;
  level: 1 | 2 | 3;
  pis: number;
  depth: number;
  volume: number;
};



export type BlastEdge = {
  src: string;
  dst: string;
  field: string;
  criticality: "hard" | "soft";
};



export type BlastRadius = {
  origin: BlastNode;
  nodes: BlastNode[];
  edges: BlastEdge[];
  summary: {
    affected_bots: number;
    aggregate_pis: number;
    patient_volume_24h: number;
    max_depth: number;
  };
  generated_at: string;
};