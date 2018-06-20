%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_home    %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy

Summary:        HA-Proxy is a TCP/HTTP reverse proxy for high availability environments
Name:           haproxy
Version:        1.8.9
Release:        1%{?dist}
License:        GPL
Group:          System Environment/Daemons
URL:            http://www.haproxy.org/
Source0:        http://www.haproxy.org/download/1.8/src/%{name}-%{version}.tar.gz
Source1:        https://raw.githubusercontent.com/AxisNL/haproxy-rpmbuild/master/SOURCES/%{name}.cfg
Source2:        https://raw.githubusercontent.com/AxisNL/haproxy-rpmbuild/master/SOURCES/%{name}.logrotate

BuildRoot:      %{_tmppath}/%{name}-%{version}-root
BuildRequires:  pcre-devel
Requires:       /sbin/chkconfig, /sbin/service

%description
This version of HAProxy is a build from the official haproxy sources,
see https://haproxy.hongens.nl.

HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
- route HTTP requests depending on statically assigned cookies
- spread the load among several servers while assuring server persistence
  through the use of HTTP cookies
- switch to backup servers in the event a main one fails
- accept connections to special ports dedicated to service monitoring
- stop accepting connections without breaking existing ones
- add/modify/delete HTTP headers both ways
- block requests matching a particular pattern

It needs very little resource. Its event-driven architecture allows it to easily
handle thousands of simultaneous connections on hundreds of instances without
risking the system's stability.

%prep
%setup -q

# We don't want any perl dependecies in this RPM:
%define __perl_requires /bin/true

%build
%{__make} USE_PCRE=1 TARGET=linux2628 USE_LINUX_TPROXY=1 USE_ZLIB=1 USE_OPENSSL=1 USE_LUA=1 LUA_LIB=/usr/local/lib LUA_INC=/usr/local/include DEBUG="" ARCH=%{_target_cpu}

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%{__make} install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}

%{__install} -d %{buildroot}%{_sbindir}
%{__install} -d %{buildroot}%{_sysconfdir}/rc.d/init.d
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}
%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{haproxy_confdir}/%{name}.cfg
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -d -m 0755 %{buildroot}%{haproxy_home}
%{__install} -s %{name} %{buildroot}%{_sbindir}/
%{__install} -c -m 755 examples/%{name}.init %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%pre
getent group %{haproxy_group} >/dev/null || groupadd -f -g 188 -r %{haproxy_group}
if ! getent passwd %{haproxy_user} >/dev/null ; then
    if ! getent passwd 188 >/dev/null ; then
        useradd -r -u 188 -g %{haproxy_group} -d %{haproxy_home} -s /sbin/nologin -c "haproxy" %{haproxy_user}
    else
        useradd -r -g %{haproxy_group} -d %{haproxy_home} -s /sbin/nologin -c "haproxy" %{haproxy_user}
    fi
fi

%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 = 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" -ge "1" ]; then
  /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc doc/* examples/
%doc CHANGELOG LICENSE README ROADMAP VERSION
%attr(0755,root,root) %{_sbindir}/%{name}
%dir %{haproxy_confdir}
%config(noreplace) %{haproxy_confdir}/%{name}.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_mandir}/man1/*
%attr(-,%{haproxy_user},%{haproxy_group}) %dir %{haproxy_home}
%attr(0755,root,root) %config %{_sysconfdir}/rc.d/init.d/%{name}
