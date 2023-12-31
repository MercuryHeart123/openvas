/* Copyright (C) 2018-2022 Greenbone AG
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

import Dashboard from '../../../components/dashboard/dashboard';

import {ResultsCvssDisplay, ResultsCvssTableDisplay} from './cvssdisplay';
import {
  ResultsDescriptionWordCloudDisplay,
  ResultsDescriptionWordCloudTableDisplay,
} from './descriptionwordclouddisplay';
import {
  ResultsSeverityDisplay,
  ResultsSeverityTableDisplay,
} from './severityclassdisplay';
import {
  ResultsWordCloudDisplay,
  ResultsWordCloudTableDisplay,
} from './wordclouddisplay';

export const RESULTS_DASHBOARD_ID = '0b8ae70d-d8fc-4418-8a72-e65ac8d2828e';

export const RESULTS_DISPLAYS = [
  ResultsCvssDisplay.displayId,
  ResultsDescriptionWordCloudDisplay.displayId,
  ResultsSeverityDisplay.displayId,
  ResultsWordCloudDisplay.displayId,
  ResultsCvssTableDisplay.displayId,
  ResultsDescriptionWordCloudTableDisplay.displayId,
  ResultsSeverityTableDisplay.displayId,
  ResultsWordCloudTableDisplay.displayId,
];

const ResultsDashboard = props => (
  <Dashboard
    {...props}
    id={RESULTS_DASHBOARD_ID}
    permittedDisplays={RESULTS_DISPLAYS}
    defaultDisplays={[
      [ResultsSeverityDisplay.displayId, ResultsCvssDisplay.displayId],
    ]}
  />
);

export default ResultsDashboard;

// vim: set ts=2 sw=2 tw=80:
