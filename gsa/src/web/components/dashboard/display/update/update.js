/* Copyright (C) 2019-2022 Greenbone AG
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

import Filter from 'gmp/models/filter';
import FilterTerm from 'gmp/models/filter/filterterm';

import { isDefined } from 'gmp/utils/identity';

import BarChart from 'web/components/chart/barchart';
import PropTypes from 'web/utils/proptypes';

import DataDisplay from '../datadisplay';
import { renderDonutChartIcons } from '../datadisplayicons';

class StatusDisplay extends React.Component {
    constructor(...args) {
        super(...args);
    }

    render() {
        const { filter, onFilterChanged, gmp, ...props } = this.props;
        return (
            <DataDisplay
                {...props}
                initialState={{
                    show3d: true,
                }}
                filter={filter}
                icons={renderDonutChartIcons}
            >
                {({ width, height, data, svgRef }) => (
                    <BarChart
                        svgRef={svgRef}
                        showLegend={false}
                        width={width}
                        // horizontal
                        gmp={gmp}
                        height={height}
                        data={{
                            nvt: {
                                label: 'NVT',
                                data: data.nvt,

                            },
                            cve: {
                                label: 'CVE',
                                data: data.cve,
                            },
                            cert: {
                                label: 'CERT',
                                data: data.cert,
                            },
                        }}
                        xLabel={'xLabel'}
                        yLabel={'yLabel'}
                        onDataClick={
                            isDefined(onFilterChanged) ? this.handleDataClick : undefined
                        }
                    />
                )}
            </DataDisplay>
        );
    }
}

StatusDisplay.propTypes = {
    filter: PropTypes.filter,
    filterTerm: PropTypes.string,
    onFilterChanged: PropTypes.func,
};

export default StatusDisplay;
