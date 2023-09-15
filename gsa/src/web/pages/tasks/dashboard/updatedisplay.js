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

import { scaleOrdinal } from 'd3-scale';

import { interpolateHcl } from 'd3-interpolate';

import { _, _l } from 'gmp/locale/lang';

import { TASKS_FILTER_FILTER } from 'gmp/models/filter';
import { getTranslatableTaskStatus, TASK_STATUS } from 'gmp/models/task';

import { registerDisplay } from 'web/components/dashboard/registry';
import { totalCount, percent } from 'web/components/dashboard/display/utils';

import createDisplay from 'web/components/dashboard/display/createDisplay';
import DataTable from 'web/components/dashboard/display/datatable';
import DataTableDisplay from 'web/components/dashboard/display/datatabledisplay'; // eslint-disable-line max-len

import update from 'web/components/dashboard/display/update/update'; // eslint-disable-line max-len

import { TasksSchedulesLoader, TasksSeverityLoader } from './loaders';

import Theme from 'web/utils/theme.js';

const red = interpolateHcl('#d62728', '#ff9896');
const green = interpolateHcl('#2ca02c', '#98df8a');
const blue = interpolateHcl('#aec7e8', '#1f77b4');
const orange = interpolateHcl('#ff7f0e', '#ffbb78');

const taskStatusColorScale = scaleOrdinal()
    .domain([
        TASK_STATUS.deleterequested,
        TASK_STATUS.ultimatedeleterequested,
        TASK_STATUS.interrupted,
        TASK_STATUS.new,
        TASK_STATUS.requested,
        TASK_STATUS.queued,
        TASK_STATUS.running,
        TASK_STATUS.stoprequested,
        TASK_STATUS.stopped,
        TASK_STATUS.done,
        'N/A',
    ])
    .range([
        red(1.0),
        red(0.5),
        red(0.0),
        green(1.0),
        green(0.5),
        Theme.severityWarnYellow,
        green(0.0),
        orange(1.0),
        orange(0.0),
        blue(0.5),
        'silver',
    ]);

const transformStatusData = (data = {}) => {
    const { groups = [] } = data;

    const sum = totalCount(groups);

    const tdata = groups.map(group => {
        const { count, value } = group;
        const translatableValue = getTranslatableTaskStatus(value);
        const perc = percent(count, sum);
        return {
            value: count,
            label: translatableValue,
            toolTip: `${translatableValue}: ${perc}% (${count})`,
            color: taskStatusColorScale(value),
            filterValue: value,
        };
    });

    tdata.total = sum;

    return tdata;
};
const getFormatedDate = () => {
    var currentDate = new Date();

    // Subtract 7 days
    currentDate.setDate(currentDate.getDate());

    // Format the date as "dd/mm/yyyy"
    var day = currentDate.getDate();
    var month = currentDate.getMonth() + 1; // Months are zero-based
    var year = currentDate.getFullYear() + 543;

    var formattedDate = day + '-' + month + '-' + year;
    return formattedDate;
}
export const UpdateDisplay = createDisplay({
    dataTransform: transformStatusData,
    displayComponent: update,
    displayId: 'update-today',
    // customeData: { title: getFormatedDate() },
    title: ({ data: tdata }) =>

        _('update by day: {{day}}', { day: tdata.total })
    ,
    filtersFilter: TASKS_FILTER_FILTER,
    loaderComponent: TasksSchedulesLoader,
});


registerDisplay(UpdateDisplay.displayId, UpdateDisplay, {
    title: _l('text: update-today'),
});

// vim: set ts=2 sw=2 tw=80:
