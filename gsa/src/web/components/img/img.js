/* Copyright (C) 2016-2022 Greenbone AG
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

import PropTypes from '../../utils/proptypes.js';

import {get_img_url} from '../../utils/urls.js';

const Img = ({alt = '', src, ...other}) => {
  const img_path = get_img_url(src);
  return <img {...other} alt={alt} src={img_path} />;
};

Img.propTypes = {
  alt: PropTypes.string,
  src: PropTypes.string.isRequired,
};

export default Img;

// vim: set ts=2 sw=2 tw=80:
