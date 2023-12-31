/* Copyright (C) 2017-2022 Greenbone AG
 *
 * SPDX-License-Identifier: AGPL-3.0-or-later
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License
 * as published by the Free Software Foundation, either version 3
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */
import React from 'react';

import _ from 'gmp/locale';

import Filter, {DFNCERT_FILTER_FILTER} from 'gmp/models/filter';

import EntitiesPage from 'web/entities/page';
import withEntitiesContainer from 'web/entities/withEntitiesContainer';

import DashboardControls from 'web/components/dashboard/controls';

import DfnCertAdvIcon from 'web/components/icon/dfncertadvicon';
import ManualIcon from 'web/components/icon/manualicon';

import PageTitle from 'web/components/layout/pagetitle';

import {
  loadEntities,
  selector as entitiesSelector,
} from 'web/store/entities/dfncerts';

import PropTypes from 'web/utils/proptypes';

// DFN-CERT uses same filter dialog as CERT-Bund
import FilterDialog from '../certbund/filterdialog';

import DfnCertTable from './table';

import DfnCertDashboard, {DFNCERT_DASHBOARD_ID} from './dashboard';

const ToolBarIcons = () => (
  <ManualIcon
    page="managing-secinfo"
    anchor="dfn-cert-advisories"
    title={_('Help: DFN-CERT Advisories')}
  />
);

const Page = ({filter, onFilterChanged, onInteraction, ...props}) => (
  <React.Fragment>
    <PageTitle title={_('DFN-CERT Advisories')} />
    <EntitiesPage
      {...props}
      createFilterType="info"
      dashboard={() => (
        <DfnCertDashboard
          filter={filter}
          onFilterChanged={onFilterChanged}
          onInteraction={onInteraction}
        />
      )}
      dashboardControls={() => (
        <DashboardControls
          dashboardId={DFNCERT_DASHBOARD_ID}
          onInteraction={onInteraction}
        />
      )}
      filter={filter}
      filterEditDialog={FilterDialog}
      filtersFilter={DFNCERT_FILTER_FILTER}
      sectionIcon={<DfnCertAdvIcon size="large" />}
      table={DfnCertTable}
      title={_('DFN-CERT Advisories')}
      toolBarIcons={ToolBarIcons}
      onFilterChanged={onFilterChanged}
      onInteraction={onInteraction}
    />
  </React.Fragment>
);

Page.propTypes = {
  filter: PropTypes.filter,
  onFilterChanged: PropTypes.func.isRequired,
  onInteraction: PropTypes.func.isRequired,
};

const fallbackFilter = Filter.fromString('sort-reverse=created');

export default withEntitiesContainer('dfncert', {
  entitiesSelector,
  fallbackFilter,
  loadEntities,
})(Page);

// vim: set ts=2 sw=2 tw=80:
