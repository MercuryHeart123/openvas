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
import _ from 'gmp/locale';
import registerCommand from 'gmp/command';
import HttpCommand from './http';
import GmpHttp from 'gmp/http/gmp';
class DjangoCommand extends HttpCommand {
    constructor(http) {
        let httpa = new GmpHttp({ apiServer: '172.31.119.130:8081/api', apiProtocol: 'http' });
        super(httpa, {
            cmd: 'get_updates',
        });
    }

    get_updates(token) {
        console.log(token);
        return this.httpGet({ token }).then(
            response => response,
            rej => {
                console.log(rej);
                throw rej;
            },
        );
    }
}

registerCommand('django', DjangoCommand);

// vim: set ts=2 sw=2 tw=80:
