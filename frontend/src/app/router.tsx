import { createBrowserRouter } from 'react-router-dom';
import Layout from '../components/Layout';
import Overview from '../pages/Overview';
import Solar from '../pages/Solar';
import Demand from '../pages/Demand';
import VPP from '../pages/VPP';
import Grid from '../pages/Grid';
import Panels from '../pages/Panels';
import Ledger from '../pages/Ledger';
import Trust from '../pages/Trust';
import Settings from '../pages/Settings';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Overview /> },
      { path: 'solar', element: <Solar /> },
      { path: 'demand', element: <Demand /> },
      { path: 'vpp', element: <VPP /> },
      { path: 'grid', element: <Grid /> },
      { path: 'panels', element: <Panels /> },
      { path: 'ledger', element: <Ledger /> },
      { path: 'trust', element: <Trust /> },
      { path: 'settings', element: <Settings /> },
      { path: '*', element: <div className="p-10"><h1 className="font-serif text-3xl">404 • Route not energized</h1><p className="mt-2 text-fg-muted">Check the path or return to Overview. Black start required.</p></div> }
    ]
  }
]);
