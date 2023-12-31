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

import HorizontalSep from 'web/components/layout/horizontalsep';

import {render} from 'web/utils/testing';

describe('HorizontalSep tests', () => {
  test('should render', () => {
    const {element} = render(<HorizontalSep />);
    expect(element).toMatchSnapshot();
  });

  test('should render with separator option', () => {
    const {element} = render(<HorizontalSep separator="|" />);
    expect(element).toMatchSnapshot();
  });

  test('should render with spacing', () => {
    const {element} = render(<HorizontalSep separator="|" spacing="10px" />);
    expect(element).toMatchSnapshot();
  });

  test('should allow to wrap', () => {
    const {element} = render(<HorizontalSep wrap />);
    expect(element).toMatchSnapshot();
  });
});
