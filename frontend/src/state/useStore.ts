import { create } from 'zustand';

type Region = any;

interface AppState {
  regionCode: string;
  regions: Region[];
  darkMode: boolean;
  setRegion: (code: string) => void;
  setRegions: (regs: Region[]) => void;
  toggleDark: () => void;
  commandOpen: boolean;
  setCommandOpen: (v: boolean) => void;
}

export const useStore = create<AppState>((set) => ({
  regionCode: 'BD',
  regions: [],
  darkMode: true,
  setRegion: (code) => set({ regionCode: code }),
  setRegions: (regs) => set({ regions: regs }),
  toggleDark: () => set((s) => ({ darkMode: !s.darkMode })),
  commandOpen: false,
  setCommandOpen: (v) => set({ commandOpen: v }),
}));
