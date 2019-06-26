%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_home    %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy

%global _hardened_build 1

Name:           haproxy
Version:        2.0.0
Release:        1%{?dist}
Summary:        TCP/HTTP proxy and load balancer for high availability environments

Group:          System Environment/Daemons
License:        GPLv2+

URL:            http://www.haproxy.org/
Source0:        http://www.haproxy.org/download/2.0/src/haproxy-%{version}.tar.gz
Source1:        https://raw.githubusercontent.com/AxisNL/haproxy-rpmbuild/master/SOURCES/%{name}.cfg
Source2:        https://raw.githubusercontent.com/AxisNL/haproxy-rpmbuild/master/SOURCES/%{name}.logrotate
Source3:        https://raw.githubusercontent.com/AxisNL/haproxy-rpmbuild/master/SOURCES/%{name}.sysconfig
Patch0:         https://raw.githubusercontent.com/AxisNL/haproxy-rpmbuild/master/SOURCES/systemdscript_prefix.patch

BuildRequires:  pcre-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
BuildRequires:  systemd-devel
BuildRequires:  systemd-units

Requires(pre):      shadow-utils
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
This version of HAProxy is a build from the official haproxy sources,
see https://haproxy.hongens.nl.

HAProxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
 - route HTTP requests depending on statically assigned cookies
 - spread load among several servers while assuring server persistence
   through the use of HTTP cookies
 - switch to backup servers in the event a main server fails
 - accept connections to special ports dedicated to service monitoring
 - stop accepting connections without breaking existing ones
 - add, modify, and delete HTTP headers in both directions
 - block requests matching particular patterns
 - report detailed status to authenticated users from a URI
   intercepted by the application

%prep
%setup -q
# patch to change the prefix in the systemd script
%patch0 -p0

%build

regparm_opts=
%ifarch %ix86 x86_64
regparm_opts="USE_REGPARM=1"
%endif

%{__make} %{?_smp_mflags} CPU="generic" TARGET="linux2628" USE_SYSTEMD=1 USE_OPENSSL=1 USE_PCRE=1 USE_ZLIB=1 USE_LUA=1 LUA_LIB=/usr/local/lib LUA_INC=/usr/local/include ${regparm_opts} ADDINC="%{optflags}" USE_LINUX_TPROXY=1 ADDLIB="%{__global_ldflags}" DEFINE=-DTCP_USER_TIMEOUT=18

pushd contrib/systemd
%{__make}
popd

%install

%{__install} -p -D -m 0644 contrib/systemd/haproxy.service %{buildroot}%{_unitdir}/%{name}.service

%{__make} install-bin DESTDIR=%{buildroot} PREFIX=%{_prefix} TARGET="linux2628"
%{__make} install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}

%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{haproxy_confdir}/%{name}.cfg
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -d -m 0755 %{buildroot}%{haproxy_home}
%{__install} -d -m 0755 %{buildroot}%{_bindir}

%{__rm} -rf ./examples/errorfiles/

find ./examples/* -type f ! -name "*.cfg" -exec %{__rm} -f "{}" \;

for textfile in $(find ./ -type f -name "*.txt" -o -name README)
do
    %{__mv} $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    %{__rm} -f $textfile.old
done

%pre
getent group %{haproxy_group} >/dev/null || groupadd -f -g 188 -r %{haproxy_group}
if ! getent passwd %{haproxy_user} >/dev/null ; then
    if ! getent passwd 188 >/dev/null ; then
        useradd -r -u 188 -g %{haproxy_group} -d %{haproxy_home} -s /sbin/nologin -c "haproxy" %{haproxy_user}
    else
        useradd -r -g %{haproxy_group} -d %{haproxy_home} -s /sbin/nologin -c "haproxy" %{haproxy_user}
    fi
fi
%{__rm} -f /etc/systemd/system/haproxy.service

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%defattr(-,root,root,-)
%doc doc/* examples/
%doc CHANGELOG LICENSE README ROADMAP VERSION
%dir %{haproxy_confdir}
%config(noreplace) %{haproxy_confdir}/%{name}.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_unitdir}/%{name}.service
%{_sbindir}/%{name}
%{_mandir}/man1/*
%attr(-,%{haproxy_user},%{haproxy_group}) %dir %{haproxy_home}
