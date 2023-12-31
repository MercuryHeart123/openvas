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

import PropTypes from '../../utils/proptypes.js';

import FormGroup from '../../components/form/formgroup.js';
import YesNoRadio from '../../components/form/yesnoradio.js';

export const AddResultsToAssetsGroup = ({inAssets, onChange}) => {
  return (
    <FormGroup title={_('Add results to Assets')}>
      <YesNoRadio name="in_assets" value={inAssets} onChange={onChange} />
    </FormGroup>
  );
};

AddResultsToAssetsGroup.propTypes = {
  inAssets: PropTypes.yesno,
  onChange: PropTypes.func,
};

export default AddResultsToAssetsGroup;

// vim: set ts=2 sw=2 tw=80:
